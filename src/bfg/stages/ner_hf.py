from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

from bfg.config import Config
from bfg.stages.base import ModelStage, StageResult


_SUBWORD_RE = re.compile(r"##")


def _has_subword_marker(word: str) -> bool:
    return "##" in (word or "")


def _strip_subword(word: str) -> str:
    return _SUBWORD_RE.sub("", word or "").strip()


def _clean_wordpiece(token: str) -> str:
    """Strip BERT WordPiece continuation markers from a single token."""

    return _strip_subword((token or "").strip())


def _merge_wordpiece(entities: Iterable[dict]) -> list[dict]:
    """Stitch orphan continuation entities back to their parent.

    The prototype leaked subwords like ##sh and ##oblot as entities. HF
    aggregation_strategy simple merges most WordPiece continuations, but
    any subword the model tags with a different label than its parent
    leaks through as its own entity.

    This pass does three things:

    1. If the current entity word starts with ## and the previous entity
       ends exactly where this one starts, merge them. Extend the previous
       word and end offset. Score becomes the min of the two.
    2. Otherwise drop the orphan.
    3. Strip stray ## markers that survive inside a token.
    """

    merged: list[dict] = []
    for e in entities:
        word = str(e.get("word", ""))
        if not word:
            continue

        is_continuation = word.lstrip().startswith("##")
        prev_end = merged[-1].get("end") if merged else None
        cur_start = e.get("start")
        touches_previous = (
            isinstance(prev_end, int)
            and isinstance(cur_start, int)
            and prev_end == cur_start
        )

        if is_continuation and touches_previous:
            prev = merged[-1]
            prev["word"] = _strip_subword(prev["word"] + word)
            prev["end"] = e.get("end", prev.get("end"))
            prev["score"] = min(float(prev.get("score", 0.0)), float(e.get("score", 0.0)))
            continue

        if is_continuation:
            # Orphan continuation with no adjacent parent. Drop it.
            continue

        cleaned = _strip_subword(word)
        if not cleaned:
            continue
        e = dict(e)
        e["word"] = cleaned
        merged.append(e)

    return merged


def _snap_to_words(text: str, entities: Iterable[dict]) -> list[dict]:
    """Rebuild each entity word from its character offsets into text.

    The pipeline reassembles the word from WordPiece tokens, so it comes
    back lowercased (d4data is uncased), with spaces around punctuation
    (il - 6), and sometimes as a fragment of a word (apical yu plus ##rt
    for apical Yurt). The offsets are exact, so the surface string is cut
    from the input and widened to whole words instead. Fragments of one
    word then share a span, and only the label with the best score is kept.
    """

    by_span: dict[tuple[int, int], dict] = {}
    for e in entities:
        start, end = e["start"], e["end"]
        while start > 0 and text[start - 1].isalnum():
            start -= 1
        while end < len(text) and text[end].isalnum():
            end += 1
        if not text[start:end].strip():
            continue
        e = {**e, "word": text[start:end], "start": start, "end": end}
        kept = by_span.get((start, end))
        if kept is None or e["score"] > kept["score"]:
            by_span[(start, end)] = e
    return [by_span[span] for span in sorted(by_span)]


def _dedupe(entities: Iterable[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    out: list[dict] = []
    for e in entities:
        key = (e.get("word", "").lower(), e.get("entity_group", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out


class HFBiomedicalNERStage(ModelStage):
    """Biomedical NER via a Hugging Face token classification pipeline.

    Default model is d4data/biomedical-ner-all, which is
    distilbert-base-uncased fine tuned on MACCROBAT clinical case reports.
    Its labels are clinical (Sign_symptom, Diagnostic_procedure, Lab_value
    and so on) rather than gene or cell line types. The pipeline hands this
    stage one combined context, the caption, then the OCR text, then the
    abstract. Inputs longer than the 512 token window are split into
    overlapping windows (cfg.ner_stride).
    """

    name = "ner"
    backend = "hf-token-cls"

    def __init__(self, cfg: Config, model_id: str) -> None:
        self.cfg = cfg
        self.model_id = model_id
        self.backend = f"hf:{model_id}"
        self._pipe = None

    def is_available(self) -> tuple[bool, str | None]:
        try:
            import torch  # noqa: F401
            from transformers import pipeline  # noqa: F401
        except ImportError as e:
            return False, f"missing python dep: {e.name}"
        return True, None

    def _load(self):
        if self._pipe is not None:
            return
        from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

        cache = str(self.cfg.ensure_cache())
        tokenizer = AutoTokenizer.from_pretrained(self.model_id, cache_dir=cache)
        model = AutoModelForTokenClassification.from_pretrained(
            self.model_id, cache_dir=cache
        )
        # A tokenizer config with no length limit disables truncation, and the
        # model then crashes on inputs longer than its position table.
        limit = getattr(model.config, "max_position_embeddings", None)
        if limit and tokenizer.model_max_length > limit:
            tokenizer.model_max_length = limit
        # stride makes the pipeline run overlapping windows over long inputs
        # instead of silently dropping everything past the first one.
        self._pipe = pipeline(
            task="token-classification",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy=self.cfg.ner_aggregation,
            stride=self.cfg.ner_stride,
        )

    def run(self, payload: Mapping[str, Any]) -> StageResult:
        text = (payload.get("text") or "").strip()
        if not text:
            return self.ok_result({"entities": [], "note": "empty context"})

        available, reason = self.is_available()
        if not available:
            return self.unavailable(reason or "transformers not available")

        try:
            self._load()
            raw = self._pipe(text)
        except Exception as e:
            return self.error(f"NER failed: {e}")

        raw_entities: list[dict[str, Any]] = []
        for item in raw or []:
            raw_entities.append(
                {
                    "word": str(item.get("word", "")),
                    "entity_group": item.get("entity_group") or item.get("entity"),
                    "score": float(item.get("score", 0.0)),
                    "start": item.get("start"),
                    "end": item.get("end"),
                }
            )

        if all(e["start"] is not None and e["end"] is not None for e in raw_entities):
            entities = _snap_to_words(text, raw_entities)
        else:
            # Slow tokenizers report no offsets, so stitch the tokens instead.
            entities = _merge_wordpiece(raw_entities)
        entities = _dedupe(entities)
        return self.ok_result({"entities": entities, "count": len(entities)})

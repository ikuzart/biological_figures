from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from bfg.config import Config
from bfg.ingest.meca import ExtractedArticle, Figure
from bfg.stages import ModelStage, StageResult, get_stage

log = logging.getLogger("bfg.pipeline")


@dataclass
class FigureAnnotation:
    fig_id: str
    label: str
    caption: str
    image_path: str
    ocr: dict[str, Any]
    vision: dict[str, Any]
    ner: dict[str, Any]


@dataclass
class ArticleAnnotation:
    article_id: str
    title: str
    abstract: str
    figures: list[FigureAnnotation] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)


@dataclass
class ContextSpan:
    """One source tagged chunk of the NER input text.

    start and end are character offsets into the assembled context string,
    so NER entities can be tagged by which source they came from.
    """

    source: str
    start: int
    end: int


def build_context(*, abstract: str, caption: str, ocr_text: str) -> str:
    """Assemble the input the NER stage runs over.

    Kept as a thin wrapper around build_context_with_spans so existing
    tests keep working. Prefer the spans variant when you need per-entity
    source attribution.
    """

    text, _ = build_context_with_spans(
        abstract=abstract, caption=caption, ocr_text=ocr_text
    )
    return text


def build_context_with_spans(
    *, abstract: str, caption: str, ocr_text: str
) -> tuple[str, list[ContextSpan]]:
    """Assemble the NER input and record where each source lives in it.

    This is where the OCR output is passed on to the NER model. Returning
    spans alongside the text lets later code work out from the character
    offsets which source each entity came from, which is how entities
    found only in the image text are counted.

    Text about this figure goes first (caption, then OCR, then abstract),
    so the sources that describe the figure lead the first window the NER
    model sees. The shared abstract comes last.
    """

    parts = [
        ("caption", caption or ""),
        ("ocr", ocr_text or ""),
        ("abstract", abstract or ""),
    ]
    chunks: list[str] = []
    spans: list[ContextSpan] = []
    cursor = 0
    for source, raw in parts:
        text = raw.strip()
        if not text:
            continue
        header = f"[{source}] "
        chunk = header + text
        if chunks:
            chunk = "\n\n" + chunk
        content_offset = cursor + len(chunk) - len(text)
        chunks.append(chunk)
        spans.append(ContextSpan(source=source, start=content_offset, end=content_offset + len(text)))
        cursor += len(chunk)
    return "".join(chunks), spans


def _source_for_offset(spans: list[ContextSpan], start: int | None) -> str | None:
    if start is None:
        return None
    for s in spans:
        if s.start <= start < s.end:
            return s.source
    return None


def _tag_entity_sources(entities: list[dict[str, Any]], spans: list[ContextSpan]) -> list[dict[str, Any]]:
    """Tag each entity with the source its start offset falls in.

    An entity with offsets outside every span sits in a [source] header
    (scispaCy tags the word caption), so it is dropped. Entities without
    offsets are kept with source set to None.
    """
    tagged: list[dict[str, Any]] = []
    for e in entities:
        source = _source_for_offset(spans, e.get("start"))
        if source is None and e.get("start") is not None:
            continue
        tagged.append({**e, "source": source})
    return tagged


def _short_hash(text: str) -> str:
    return hashlib.sha1((text or "").encode("utf-8")).hexdigest()[:12]


def _payload_hash(payload: dict[str, Any]) -> str:
    """Deterministic hash of a stage payload for the log stream."""
    if "text" in payload:
        return _short_hash(payload["text"] or "")
    if "image_path" in payload:
        return _short_hash(str(payload["image_path"]))
    return _short_hash(json.dumps(payload, sort_keys=True, default=str))


def _output_length(result: StageResult) -> int:
    data = result.data or {}
    for key in ("text", "caption"):
        if key in data:
            return len(str(data[key] or ""))
    if "count" in data:
        return int(data["count"])
    return 0


def _log_stage_event(
    log_path: Path | None,
    *,
    article_id: str,
    fig_id: str,
    stage: ModelStage,
    payload: dict[str, Any],
    result: StageResult,
    elapsed_s: float,
) -> None:
    if log_path is None:
        return
    record = {
        "article_id": article_id,
        "fig_id": fig_id,
        "stage": stage.name,
        "backend": stage.backend,
        "input_hash": _payload_hash(payload),
        "output_length": _output_length(result),
        "elapsed_s": round(elapsed_s, 4),
        "status": result.status.value,
        "detail": result.detail,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _run_stage(
    stage: ModelStage,
    payload: dict[str, Any],
    *,
    article_id: str = "",
    fig_id: str = "",
    log_path: Path | None = None,
) -> StageResult:
    started = time.perf_counter()
    available, reason = stage.is_available()
    if not available:
        log.info("%s/%s unavailable: %s", stage.name, stage.backend, reason)
        result = stage.unavailable(reason or "unavailable")
    else:
        result = stage.run(payload)
    elapsed = time.perf_counter() - started
    _log_stage_event(
        log_path,
        article_id=article_id,
        fig_id=fig_id,
        stage=stage,
        payload=payload,
        result=result,
        elapsed_s=elapsed,
    )
    return result


def _annotate_figure(
    figure: Figure,
    abstract: str,
    ocr: ModelStage,
    vision: ModelStage,
    ner: ModelStage,
    *,
    article_id: str = "",
    log_path: Path | None = None,
) -> FigureAnnotation:
    image_payload = {"image_path": str(figure.image_path)}

    ocr_result = _run_stage(
        ocr, image_payload,
        article_id=article_id, fig_id=figure.fig_id, log_path=log_path,
    )
    vision_result = _run_stage(
        vision, image_payload,
        article_id=article_id, fig_id=figure.fig_id, log_path=log_path,
    )

    ocr_text = ocr_result.data.get("text", "") if ocr_result.ok else ""
    context, spans = build_context_with_spans(
        abstract=abstract, caption=figure.caption, ocr_text=ocr_text
    )
    ner_result = _run_stage(
        ner, {"text": context},
        article_id=article_id, fig_id=figure.fig_id, log_path=log_path,
    )

    if ner_result.ok:
        entities = ner_result.data.get("entities", []) or []
        tagged = _tag_entity_sources(list(entities), spans)
        ner_dict = ner_result.to_dict()
        ner_dict["data"] = dict(ner_dict["data"])
        ner_dict["data"]["entities"] = tagged
    else:
        ner_dict = ner_result.to_dict()

    return FigureAnnotation(
        fig_id=figure.fig_id,
        label=figure.label,
        caption=figure.caption,
        image_path=str(figure.image_path),
        ocr=ocr_result.to_dict(),
        vision=vision_result.to_dict(),
        ner=ner_dict,
    )


def annotate_article(
    article: ExtractedArticle,
    cfg: Config | None = None,
    stages: dict[str, ModelStage] | None = None,
    *,
    log_path: Path | str | None = None,
) -> ArticleAnnotation:
    """Run the full three stage pipeline over every figure in article.

    stages lets tests inject fakes. Production uses the registry keyed by
    cfg. When log_path is provided, each stage invocation appends a JSONL
    record with article_id, fig_id, stage, backend, input hash, output
    length, elapsed time, and status.
    """

    cfg = cfg or Config()
    if stages is None:
        stages = {
            "ocr": get_stage(cfg.ocr_backend, cfg),
            "vision": get_stage(cfg.vision_backend, cfg),
            "ner": get_stage(cfg.ner_backend, cfg),
        }

    resolved_log = Path(log_path) if log_path is not None else None

    figures = [
        _annotate_figure(
            fig,
            article.abstract,
            stages["ocr"],
            stages["vision"],
            stages["ner"],
            article_id=article.article_id,
            log_path=resolved_log,
        )
        for fig in article.figures
    ]

    return ArticleAnnotation(
        article_id=article.article_id,
        title=article.title,
        abstract=article.abstract,
        figures=figures,
    )


def write_annotation(annotation: ArticleAnnotation, out_path: Path | str) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(annotation.to_json(), encoding="utf-8")
    return out

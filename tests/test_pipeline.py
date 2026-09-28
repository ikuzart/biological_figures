import json
from pathlib import Path
from typing import Any, Mapping

from bfg.config import Config
from bfg.ingest.meca import ExtractedArticle, Figure
from bfg.pipeline.annotator import (
    annotate_article,
    build_context,
    build_context_with_spans,
    _tag_entity_sources,
)
from bfg.stages.base import ModelStage, StageResult


class FakeOCR(ModelStage):
    name = "ocr"
    backend = "fake-ocr"

    def is_available(self):
        return True, None

    def run(self, payload: Mapping[str, Any]) -> StageResult:
        return self.ok_result({"text": "IB: GAPDH 75 kDa", "char_count": 16})


class FakeVision(ModelStage):
    name = "vision"
    backend = "fake-vision"

    def is_available(self):
        return True, None

    def run(self, payload: Mapping[str, Any]) -> StageResult:
        return self.ok_result({"caption": "a series of photos of refrigerators"})


class FakeNER(ModelStage):
    name = "ner"
    backend = "fake-ner"

    def __init__(self):
        self.last_text: str | None = None

    def is_available(self):
        return True, None

    def run(self, payload: Mapping[str, Any]) -> StageResult:
        self.last_text = payload.get("text", "")
        return self.ok_result(
            {"entities": [{"word": "p66Shc", "entity_group": "gene"}], "count": 1}
        )


class UnavailableNER(ModelStage):
    name = "ner"
    backend = "unavailable"

    def is_available(self):
        return False, "not installed"

    def run(self, payload: Mapping[str, Any]) -> StageResult:  # pragma: no cover
        raise AssertionError("run() should not be called for unavailable stages")


class ExplodingOCR(ModelStage):
    name = "ocr"
    backend = "boom"

    def is_available(self):
        return True, None

    def run(self, payload: Mapping[str, Any]) -> StageResult:
        return self.error("simulated failure")


def _article(tmp_path: Path) -> ExtractedArticle:
    img = tmp_path / "fig1.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    fig = Figure(
        fig_id="fig1",
        label="Figure 1",
        caption="p66Shc mediates SUMO2-induced ROS production.",
        image_path=img,
    )
    return ExtractedArticle(
        article_id="577109",
        title="p66Shc Mediates SUMO2-induced Endothelial Dysfunction",
        abstract="Hyperlipidemia induces endothelial dysfunction via p66Shc.",
        figures=[fig],
    )


def test_build_context_bundles_all_three_sources():
    ctx = build_context(
        abstract="an abstract", caption="a caption", ocr_text="ocr text"
    )
    assert "[abstract] an abstract" in ctx
    assert "[caption] a caption" in ctx
    assert "[ocr] ocr text" in ctx


def test_build_context_skips_empty_sources():
    ctx = build_context(abstract="", caption="cap", ocr_text="")
    assert ctx == "[caption] cap"


def test_pipeline_hands_ocr_plus_caption_plus_abstract_to_ner(tmp_path: Path):
    ner = FakeNER()
    stages = {"ocr": FakeOCR(), "vision": FakeVision(), "ner": ner}
    result = annotate_article(_article(tmp_path), Config(), stages)

    assert len(result.figures) == 1
    ann = result.figures[0]
    assert ann.ocr["status"] == "ok"
    assert ann.vision["status"] == "ok"
    assert ann.ner["status"] == "ok"

    assert ner.last_text is not None
    assert "IB: GAPDH" in ner.last_text
    assert "SUMO2" in ner.last_text
    assert "Hyperlipidemia" in ner.last_text


def test_pipeline_is_fail_soft_when_stage_unavailable(tmp_path: Path):
    stages = {"ocr": FakeOCR(), "vision": FakeVision(), "ner": UnavailableNER()}
    result = annotate_article(_article(tmp_path), Config(), stages)
    ann = result.figures[0]
    assert ann.ner["status"] == "unavailable"
    assert ann.ocr["status"] == "ok"


def test_pipeline_survives_stage_error(tmp_path: Path):
    stages = {"ocr": ExplodingOCR(), "vision": FakeVision(), "ner": FakeNER()}
    result = annotate_article(_article(tmp_path), Config(), stages)
    ann = result.figures[0]
    assert ann.ocr["status"] == "error"
    assert ann.vision["status"] == "ok"
    assert ann.ner["status"] == "ok"


def test_build_context_with_spans_records_offsets():
    text, spans = build_context_with_spans(
        abstract="an abstract", caption="a caption", ocr_text="ocr text"
    )
    by_source = {s.source: s for s in spans}
    assert set(by_source) == {"abstract", "caption", "ocr"}
    for source, span in by_source.items():
        assert text[span.start:span.end] == {
            "abstract": "an abstract",
            "caption": "a caption",
            "ocr": "ocr text",
        }[source]


def test_build_context_puts_figure_text_before_abstract():
    text, spans = build_context_with_spans(
        abstract="an abstract", caption="a caption", ocr_text="ocr text"
    )
    assert [s.source for s in spans] == ["caption", "ocr", "abstract"]
    assert text.startswith("[caption] a caption")


def test_build_context_with_spans_skips_empty_sources():
    text, spans = build_context_with_spans(
        abstract="", caption="cap", ocr_text=""
    )
    assert text == "[caption] cap"
    assert len(spans) == 1
    assert spans[0].source == "caption"


class OffsetTaggingNER(ModelStage):
    """Emits one entity per source section tagged with the exact char offset
    of that section's content start. The pipeline source tagging pass should
    turn those offsets into abstract, caption, or ocr labels.
    """

    name = "ner"
    backend = "offset-tagging-ner"

    def is_available(self):
        return True, None

    def run(self, payload: Mapping[str, Any]) -> StageResult:
        text = payload.get("text", "")
        entities = []
        for source in ("abstract", "caption", "ocr"):
            header = f"[{source}] "
            i = text.find(header)
            if i == -1:
                continue
            content_start = i + len(header)
            entities.append(
                {
                    "word": f"marker-{source}",
                    "entity_group": "marker",
                    "score": 1.0,
                    "start": content_start,
                    "end": content_start + 1,
                }
            )
        return self.ok_result({"entities": entities, "count": len(entities)})


def test_pipeline_tags_each_entity_with_its_source(tmp_path: Path):
    stages = {"ocr": FakeOCR(), "vision": FakeVision(), "ner": OffsetTaggingNER()}
    result = annotate_article(_article(tmp_path), Config(), stages)
    entities = result.figures[0].ner["data"]["entities"]
    tagged = {e["word"]: e["source"] for e in entities}
    assert tagged == {
        "marker-abstract": "abstract",
        "marker-caption": "caption",
        "marker-ocr": "ocr",
    }


def test_tag_entity_sources_drops_entities_in_headers():
    text, spans = build_context_with_spans(abstract="", caption="GFP-Yurt", ocr_text="")
    entities = [
        {"word": "caption", "start": 1, "end": 8},  # the header word itself
        {"word": "GFP-Yurt", "start": text.index("GFP"), "end": len(text)},
        {"word": "Yurt", "start": None, "end": None},
    ]
    tagged = _tag_entity_sources(entities, spans)
    assert [(e["word"], e["source"]) for e in tagged] == [("GFP-Yurt", "caption"), ("Yurt", None)]


def test_pipeline_writes_jsonl_stage_log(tmp_path: Path):
    log_path = tmp_path / "logs" / "pipeline.jsonl"
    stages = {"ocr": FakeOCR(), "vision": FakeVision(), "ner": FakeNER()}
    annotate_article(_article(tmp_path), Config(), stages, log_path=log_path)

    assert log_path.exists()
    lines = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert len(lines) == 3
    stages_seen = [r["stage"] for r in lines]
    assert stages_seen == ["ocr", "vision", "ner"]
    for r in lines:
        assert r["article_id"] == "577109"
        assert r["fig_id"] == "fig1"
        assert r["status"] == "ok"
        assert isinstance(r["input_hash"], str) and len(r["input_hash"]) == 12
        assert isinstance(r["elapsed_s"], float)
        assert r["output_length"] >= 0

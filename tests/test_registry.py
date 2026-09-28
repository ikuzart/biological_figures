import pytest

from bfg.config import Config
from bfg.stages.registry import REGISTRY, get_stage, specs_for_modality


def test_registry_has_default_backends():
    keys = set(REGISTRY)
    assert "tesseract" in keys
    assert "vit-gpt2" in keys
    assert "d4data-biomedical-ner-all" in keys


def test_registry_covers_three_modalities():
    modalities = {spec.modality for spec in REGISTRY.values()}
    assert modalities == {"ocr", "vision", "ner"}


def test_specs_for_modality_filters():
    assert {s.key for s in specs_for_modality("ocr")} >= {"tesseract", "trocr"}
    assert {s.key for s in specs_for_modality("ner")} >= {
        "d4data-biomedical-ner-all",
        "scispacy",
        "bert-base-ner",
    }
    assert {s.key for s in specs_for_modality("vision")} >= {"vit-gpt2", "blip"}


def test_registry_exposes_bert_base_ner_control():
    """dslim/bert-base-NER is registered as the NER control. It is fine-tuned
    on CoNLL-2003 news, where d4data is fine-tuned on clinical case reports."""
    assert "bert-base-ner" in REGISTRY
    stage = get_stage("bert-base-ner", Config())
    assert stage.name == "ner"
    assert "dslim/bert-base-NER" in stage.backend


def test_get_stage_rejects_unknown_key():
    with pytest.raises(KeyError):
        get_stage("no-such-backend", Config())


def test_get_stage_returns_expected_type():
    from bfg.stages.ocr_tesseract import TesseractOCRStage

    stage = get_stage("tesseract", Config())
    assert isinstance(stage, TesseractOCRStage)
    assert stage.name == "ocr"

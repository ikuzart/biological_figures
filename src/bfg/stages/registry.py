from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from bfg.config import Config
from bfg.stages.base import ModelStage


@dataclass(frozen=True)
class StageSpec:
    """Metadata about a swappable backend for one pipeline stage.

    The modality field is one of ocr, vision, or ner. Used by the CLI to
    list candidates for a given stage.
    """

    key: str
    modality: str
    description: str
    factory: Callable[[Config], ModelStage]


def _build_tesseract(cfg: Config) -> ModelStage:
    from bfg.stages.ocr_tesseract import TesseractOCRStage

    return TesseractOCRStage(cfg)


def _build_trocr(cfg: Config) -> ModelStage:
    from bfg.stages.ocr_trocr import TrOCRStage

    return TrOCRStage(cfg)


def _build_vit_gpt2(cfg: Config) -> ModelStage:
    from bfg.stages.vision_vit_gpt2 import ViTGPT2VisionStage

    return ViTGPT2VisionStage(cfg)


def _build_blip(cfg: Config) -> ModelStage:
    from bfg.stages.vision_blip import BLIPVisionStage

    return BLIPVisionStage(cfg)


def _build_d4data_ner(cfg: Config) -> ModelStage:
    from bfg.stages.ner_hf import HFBiomedicalNERStage

    return HFBiomedicalNERStage(cfg, model_id="d4data/biomedical-ner-all")


def _build_scispacy(cfg: Config) -> ModelStage:
    from bfg.stages.ner_scispacy import SciSpacyNERStage

    return SciSpacyNERStage(cfg)


def _build_bert_ner(cfg: Config) -> ModelStage:
    from bfg.stages.ner_hf import HFBiomedicalNERStage

    return HFBiomedicalNERStage(cfg, model_id="dslim/bert-base-NER")


REGISTRY: dict[str, StageSpec] = {
    "tesseract": StageSpec(
        key="tesseract",
        modality="ocr",
        description="Tesseract LSTM OCR, baseline, CPU only.",
        factory=_build_tesseract,
    ),
    "trocr": StageSpec(
        key="trocr",
        modality="ocr",
        description="microsoft/trocr-base-printed, benchmark candidate.",
        factory=_build_trocr,
    ),
    "vit-gpt2": StageSpec(
        key="vit-gpt2",
        modality="vision",
        description="nlpconnect/vit-gpt2-image-captioning, general domain captioner.",
        factory=_build_vit_gpt2,
    ),
    "blip": StageSpec(
        key="blip",
        modality="vision",
        description="Salesforce/blip-image-captioning-base, second general captioner.",
        factory=_build_blip,
    ),
    "d4data-biomedical-ner-all": StageSpec(
        key="d4data-biomedical-ner-all",
        modality="ner",
        description="d4data/biomedical-ner-all (DistilBERT, MACCROBAT clinical labels).",
        factory=_build_d4data_ner,
    ),
    "scispacy": StageSpec(
        key="scispacy",
        modality="ner",
        description="scispaCy en_core_sci_lg, lightweight comparison target.",
        factory=_build_scispacy,
    ),
    "bert-base-ner": StageSpec(
        key="bert-base-ner",
        modality="ner",
        description="dslim/bert-base-NER, general domain NER control.",
        factory=_build_bert_ner,
    ),
}


def get_stage(key: str, cfg: Config) -> ModelStage:
    if key not in REGISTRY:
        known = ", ".join(sorted(REGISTRY))
        raise KeyError(f"Unknown stage backend '{key}'. Known: {known}")
    return REGISTRY[key].factory(cfg)


def specs_for_modality(modality: str) -> list[StageSpec]:
    return [s for s in REGISTRY.values() if s.modality == modality]

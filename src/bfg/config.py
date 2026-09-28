import os
from dataclasses import dataclass, field
from pathlib import Path


def _default_cache() -> Path:
    env = os.getenv("BFG_MODEL_CACHE")
    if env:
        return Path(env).expanduser().resolve()
    return (Path(__file__).resolve().parents[2] / "hf_models").resolve()


@dataclass
class Config:
    """Runtime configuration for the pipeline.

    Backends are pluggable via the model registry so stages can be swapped
    without touching the pipeline, for example Tesseract vs TrOCR,
    or d4data vs scispaCy.
    """

    model_cache: Path = field(default_factory=_default_cache)

    ocr_backend: str = "tesseract"
    vision_backend: str = "vit-gpt2"
    ner_backend: str = "d4data-biomedical-ner-all"

    ocr_language: str = "eng"
    ner_aggregation: str = "simple"
    ner_stride: int = 128
    vision_max_new_tokens: int = 40

    def ensure_cache(self) -> Path:
        self.model_cache.mkdir(parents=True, exist_ok=True)
        return self.model_cache

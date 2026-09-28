from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from bfg.config import Config
from bfg.stages.base import ModelStage, StageResult


class TrOCRStage(ModelStage):
    """TrOCR (Li et al., 2023), benchmark candidate against Tesseract.

    Not enabled by default. The CLI can select it as an alternative OCR
    backend via --ocr trocr to test whether transformer OCR handles
    rotated and varied layout figure text better than Tesseract.
    """

    name = "ocr"
    backend = "trocr"

    MODEL_ID = "microsoft/trocr-base-printed"

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self._model = None
        self._processor = None

    def is_available(self) -> tuple[bool, str | None]:
        try:
            import torch  # noqa: F401
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel  # noqa: F401
            from PIL import Image  # noqa: F401
        except ImportError as e:
            return False, f"missing python dep: {e.name}"
        return True, None

    def _load(self):
        if self._model is not None:
            return
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel

        cache = str(self.cfg.ensure_cache())
        self._processor = TrOCRProcessor.from_pretrained(self.MODEL_ID, cache_dir=cache)
        self._model = VisionEncoderDecoderModel.from_pretrained(
            self.MODEL_ID, cache_dir=cache
        )

    def run(self, payload: Mapping[str, Any]) -> StageResult:
        image_path = payload.get("image_path")
        if not image_path:
            return self.error("no image_path in payload")

        available, reason = self.is_available()
        if not available:
            return self.unavailable(reason or "trocr not available")

        try:
            from PIL import Image

            self._load()
            with Image.open(Path(image_path)) as img:
                pixel_values = self._processor(
                    images=img.convert("RGB"), return_tensors="pt"
                ).pixel_values
                ids = self._model.generate(pixel_values)
            text = self._processor.batch_decode(ids, skip_special_tokens=True)[0]
        except Exception as e:
            return self.error(f"TrOCR failed: {e}")

        text = (text or "").strip()
        return self.ok_result({"text": text, "char_count": len(text)})

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Mapping

from bfg.config import Config
from bfg.stages.base import ModelStage, StageResult


class TesseractOCRStage(ModelStage):
    """Image to embedded text via the Tesseract LSTM engine.

    Recovers antibody labels, molecular weight markers, species names and
    pathway identifiers from figures. Missed rotated axis labels are a
    known limitation.
    """

    name = "ocr"
    backend = "tesseract"

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg

    def is_available(self) -> tuple[bool, str | None]:
        if shutil.which("tesseract") is None:
            return False, "tesseract binary not found on PATH"
        try:
            import pytesseract  # noqa: F401
            from PIL import Image  # noqa: F401
        except ImportError as e:
            return False, f"missing python dep: {e.name}"
        return True, None

    def run(self, payload: Mapping[str, Any]) -> StageResult:
        image_path = payload.get("image_path")
        if not image_path:
            return self.error("no image_path in payload")

        available, reason = self.is_available()
        if not available:
            return self.unavailable(reason or "tesseract not available")

        import pytesseract
        from PIL import Image

        try:
            with Image.open(Path(image_path)) as img:
                text = pytesseract.image_to_string(img, lang=self.cfg.ocr_language)
        except Exception as e:
            return self.error(f"OCR failed: {e}")

        text = (text or "").strip()
        return self.ok_result({"text": text, "char_count": len(text)})

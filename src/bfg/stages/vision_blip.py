from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from bfg.config import Config
from bfg.stages.base import ModelStage, StageResult


class BLIPVisionStage(ModelStage):
    """BLIP (Li et al., 2022), a second general domain captioner.

    Trained separately from ViT-GPT2 and with a different method, so it
    shows whether the domain gap belongs to one model or to general
    captioners as a whole.
    """

    name = "vision"
    backend = "blip"

    MODEL_ID = "Salesforce/blip-image-captioning-base"

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self._model = None
        self._processor = None

    def is_available(self) -> tuple[bool, str | None]:
        try:
            import torch  # noqa: F401
            from transformers import BlipForConditionalGeneration, BlipProcessor  # noqa: F401
            from PIL import Image  # noqa: F401
        except ImportError as e:
            return False, f"missing python dep: {e.name}"
        return True, None

    def _load(self):
        if self._model is not None:
            return
        from transformers import BlipForConditionalGeneration, BlipProcessor

        cache = str(self.cfg.ensure_cache())
        self._processor = BlipProcessor.from_pretrained(self.MODEL_ID, cache_dir=cache)
        self._model = BlipForConditionalGeneration.from_pretrained(
            self.MODEL_ID, cache_dir=cache
        )

    def run(self, payload: Mapping[str, Any]) -> StageResult:
        image_path = payload.get("image_path")
        if not image_path:
            return self.error("no image_path in payload")

        available, reason = self.is_available()
        if not available:
            return self.unavailable(reason or "blip not available")

        try:
            import torch
            from PIL import Image

            self._load()
            with Image.open(Path(image_path)) as img:
                inputs = self._processor(images=img.convert("RGB"), return_tensors="pt")
            with torch.no_grad():
                ids = self._model.generate(
                    **inputs, max_new_tokens=self.cfg.vision_max_new_tokens
                )
            caption = self._processor.batch_decode(ids, skip_special_tokens=True)[0]
        except Exception as e:
            return self.error(f"BLIP caption failed: {e}")

        caption = (caption or "").strip()
        return self.ok_result({"caption": caption})

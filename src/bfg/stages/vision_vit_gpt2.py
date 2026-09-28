from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from bfg.config import Config
from bfg.stages.base import ModelStage, StageResult


class ViTGPT2VisionStage(ModelStage):
    """Image to natural language caption via nlpconnect/vit-gpt2-image-captioning.

    Kept as the baseline vision backend even though the prototype scored
    a Jaccard of 0.000 against the real captions of biomedical figures.
    Keeping it is what makes the domain gap measurable. A domain aware
    captioner would replace it behind the same interface.
    """

    name = "vision"
    backend = "vit-gpt2"

    MODEL_ID = "nlpconnect/vit-gpt2-image-captioning"

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self._model = None
        self._processor = None
        self._tokenizer = None

    def is_available(self) -> tuple[bool, str | None]:
        try:
            import torch  # noqa: F401
            from transformers import (  # noqa: F401
                AutoTokenizer,
                VisionEncoderDecoderModel,
                ViTImageProcessor,
            )
            from PIL import Image  # noqa: F401
        except ImportError as e:
            return False, f"missing python dep: {e.name}"
        return True, None

    def _load(self):
        if self._model is not None:
            return
        from transformers import (
            AutoTokenizer,
            VisionEncoderDecoderModel,
            ViTImageProcessor,
        )

        cache = str(self.cfg.ensure_cache())
        self._model = VisionEncoderDecoderModel.from_pretrained(
            self.MODEL_ID, cache_dir=cache
        )
        self._processor = ViTImageProcessor.from_pretrained(
            self.MODEL_ID, cache_dir=cache
        )
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.MODEL_ID, cache_dir=cache
        )

    def run(self, payload: Mapping[str, Any]) -> StageResult:
        image_path = payload.get("image_path")
        if not image_path:
            return self.error("no image_path in payload")

        available, reason = self.is_available()
        if not available:
            return self.unavailable(reason or "vit-gpt2 not available")

        try:
            import torch
            from PIL import Image

            self._load()
            with Image.open(Path(image_path)) as img:
                pixel_values = self._processor(
                    images=img.convert("RGB"), return_tensors="pt"
                ).pixel_values

            with torch.no_grad():
                ids = self._model.generate(
                    pixel_values, max_new_tokens=self.cfg.vision_max_new_tokens
                )
            caption = self._tokenizer.batch_decode(ids, skip_special_tokens=True)[0]
        except Exception as e:
            return self.error(f"vision caption failed: {e}")

        caption = (caption or "").strip()
        return self.ok_result({"caption": caption})

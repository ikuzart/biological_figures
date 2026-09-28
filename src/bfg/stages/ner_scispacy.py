from __future__ import annotations

from typing import Any, Mapping

from bfg.config import Config
from bfg.stages.base import ModelStage, StageResult


class SciSpacyNERStage(ModelStage):
    """scispaCy NER, comparison target for the HF biomedical model.

    Needs a scispaCy model installed separately, for example en_core_sci_lg.
    The evaluation plan compares this against d4data on entity type breakdowns
    rather than aggregate F1.
    """

    name = "ner"
    backend = "scispacy"

    MODEL_NAME = "en_core_sci_lg"

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self._nlp = None

    def is_available(self) -> tuple[bool, str | None]:
        try:
            import spacy  # noqa: F401
        except ImportError as e:
            return False, f"missing python dep: {e.name}"
        try:
            import spacy

            spacy.util.get_installed_models()
        except Exception as e:
            return False, f"spacy misconfigured: {e}"
        return True, None

    def _load(self):
        if self._nlp is not None:
            return
        import spacy

        try:
            self._nlp = spacy.load(self.MODEL_NAME)
        except OSError as e:
            raise RuntimeError(
                f"scispaCy model '{self.MODEL_NAME}' not installed. "
                "See https://allenai.github.io/scispacy/"
            ) from e

    def run(self, payload: Mapping[str, Any]) -> StageResult:
        text = (payload.get("text") or "").strip()
        if not text:
            return self.ok_result({"entities": [], "note": "empty context"})

        available, reason = self.is_available()
        if not available:
            return self.unavailable(reason or "scispacy not available")

        try:
            self._load()
            doc = self._nlp(text)
        except Exception as e:
            return self.error(f"scispaCy NER failed: {e}")

        entities = [
            {
                "word": ent.text,
                "entity_group": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            }
            for ent in doc.ents
        ]
        return self.ok_result({"entities": entities, "count": len(entities)})

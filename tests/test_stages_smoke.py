"""Smoke tests for every backend registered in the stage registry.

Each backend is exercised via its public ModelStage contract:

- is_available() returns (bool, reason).
- run(payload) returns a StageResult with a valid StageStatus, a dict
  data field, and never raises.

When a backend's dependencies are not installed on the test machine, for
example scispaCy without spacy, or TrOCR without torch binaries, it must
report unavailable via is_available() and the run() call must return a
StageResult with status unavailable or error, never crash.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from bfg.config import Config
from bfg.stages import ModelStage, StageResult, StageStatus, get_stage
from bfg.stages.registry import REGISTRY


def _tiny_png(path: Path) -> Path:
    """Write a minimal valid 1x1 PNG so image stage code has real bytes."""
    path.write_bytes(
        bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
            "890000000d49444154789c626001000000ffff03000006000557bf9c9f000000"
            "0049454e44ae426082"
        )
    )
    return path


def _payload_for(modality: str, tmp_path: Path) -> dict:
    if modality in {"ocr", "vision"}:
        return {"image_path": str(_tiny_png(tmp_path / "smoke.png"))}
    return {"text": "p66Shc mediates SUMO2-induced endothelial dysfunction."}


@pytest.mark.parametrize("key", sorted(REGISTRY.keys()))
def test_stage_contract(key: str, tmp_path: Path):
    spec = REGISTRY[key]
    stage: ModelStage = get_stage(key, Config())

    assert stage.name == spec.modality
    assert isinstance(stage.backend, str) and stage.backend

    available, reason = stage.is_available()
    assert isinstance(available, bool)
    if not available:
        assert isinstance(reason, str) and reason

    payload = _payload_for(spec.modality, tmp_path)
    result = stage.run(payload)
    assert isinstance(result, StageResult)
    assert isinstance(result.status, StageStatus)
    assert isinstance(result.data, dict)
    if result.status is StageStatus.OK:
        assert result.data
    else:
        assert result.detail

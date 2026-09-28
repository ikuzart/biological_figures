from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class StageStatus(str, Enum):
    OK = "ok"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


@dataclass
class StageResult:
    """Uniform result payload every ModelStage returns.

    Unavailable and error results carry a readable detail string so the
    pipeline can carry on with the other stages rather than crash.
    """

    stage: str
    backend: str
    status: StageStatus
    data: Mapping[str, Any] = field(default_factory=dict)
    detail: str | None = None

    @property
    def ok(self) -> bool:
        return self.status is StageStatus.OK

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "backend": self.backend,
            "status": self.status.value,
            "data": dict(self.data),
            "detail": self.detail,
        }


class ModelStage(ABC):
    """Common interface for every pipeline stage.

    The pipeline only relies on is_available() and run(payload). This
    keeps stages independently testable and lets the pipeline degrade
    gracefully when a backend is missing.
    """

    name: str = "stage"
    backend: str = "unknown"

    @abstractmethod
    def is_available(self) -> tuple[bool, str | None]:
        """Return (available, reason). Reason is only set when False."""

    @abstractmethod
    def run(self, payload: Mapping[str, Any]) -> StageResult:
        """Run the stage. Must never raise. Return an error result on any exception."""

    def unavailable(self, reason: str) -> StageResult:
        return StageResult(
            stage=self.name,
            backend=self.backend,
            status=StageStatus.UNAVAILABLE,
            detail=reason,
        )

    def error(self, reason: str) -> StageResult:
        return StageResult(
            stage=self.name,
            backend=self.backend,
            status=StageStatus.ERROR,
            detail=reason,
        )

    def ok_result(self, data: Mapping[str, Any]) -> StageResult:
        return StageResult(
            stage=self.name,
            backend=self.backend,
            status=StageStatus.OK,
            data=data,
        )

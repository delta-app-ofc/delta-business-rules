"""Estruturas de dados compartilhadas pelas regras de negócio."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ConsumptionPoint:
    """Uma janela de consumption_summary (MongoDB)."""

    user_id: int
    window_started_at: datetime
    window_finished_at: datetime
    consumption_liters: float
    anomaly_detected: bool
    lpm_average: float | None = None
    device_id: str | None = None

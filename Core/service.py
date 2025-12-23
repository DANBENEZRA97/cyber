# Core/service.py
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Service:
    service_id: str
    name: str
    avg_minutes: int

    def update_avg_minutes(self, minutes: int) -> None:
        if minutes <= 0:
            raise ValueError("avg_minutes must be positive")
        self.avg_minutes = minutes

    def display(self) -> str:
        return f"{self.name} (avg {self.avg_minutes} min)"

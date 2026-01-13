# Core/mixins.py
from __future__ import annotations
from datetime import datetime
from typing import List


class AuditMixin:
    """Mixin: Logic for audit logging."""
    def __init__(self) -> None:
        self.audit_log: List[str] = []  # list

    def log(self, message: str) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.audit_log.append(f"[{ts}] {message}")

    def get_audit_log(self) -> List[str]:
        return list(self.audit_log)


class NotifiableMixin:
    """Mixin: Logic for notifications."""
    def notify(self, message: str) -> None:
        print(f"NOTIFY: {message}")

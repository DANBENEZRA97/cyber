# Core/mixins.py
from __future__ import annotations
from datetime import datetime
from typing import List


class AuditMixin:
    """Mixin: מוסיף audit_log + פעולות לוגיות של תיעוד."""
    def __init__(self) -> None:
        self.audit_log: List[str] = []  # list (דרישה)

    def log(self, message: str) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.audit_log.append(f"[{ts}] {message}")

    def get_audit_log(self) -> List[str]:
        return list(self.audit_log)


class NotifiableMixin:
    """Mixin: מדמה יכולת הודעה למשתמש (בהמשך GUI יכול להחליף)."""
    def notify(self, message: str) -> None:
        print(f"NOTIFY: {message}")

# Core/mixins.py
from __future__ import annotations
from datetime import datetime
from typing import List
from tkinter import messagebox
import tkinter as tk


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
    def notify(self, message: str) -> None:
        """
        Show a small GUI notification if a Tk root exists.
        Fallback to print() if GUI is not running.
        """
        try:
            # Check if there is an active Tk root window
            if tk._default_root is not None:
                messagebox.showinfo("Notification", message)
            else:
                print(f"[NOTIFY] {message}")
        except Exception:
            print(f"[NOTIFY] {message}")
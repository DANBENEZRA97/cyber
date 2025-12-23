# Core/ticket.py
from __future__ import annotations
from datetime import datetime
from Core.mixins import AuditMixin, NotifiableMixin


class Ticket(AuditMixin, NotifiableMixin):  # Multiple Inheritance
    def __init__(self, ticket_id: str, customer_id: str, service_id: str, priority: int = 0) -> None:
        AuditMixin.__init__(self)
        self.ticket_id: str = ticket_id
        self.customer_id: str = customer_id
        self.service_id: str = service_id

        self.created_at: datetime = datetime.now()
        self.status: str = "WAITING"  # WAITING / CALLED / DONE / CANCELED
        self.priority: int = int(priority)  # 0/1 (חדש)

        self.log(f"Ticket created (customer={customer_id}, service={service_id}, priority={self.priority})")

    def set_priority(self, new_priority: int) -> None:
        new_priority = int(new_priority)
        if new_priority not in (0, 1):
            raise ValueError("Priority must be 0 or 1")
        if self.status != "WAITING":
            raise ValueError("Can change priority only while ticket is WAITING")
        old = self.priority
        self.priority = new_priority
        self.log(f"Priority changed {old} -> {new_priority}")

    def mark_called(self) -> None:
        if self.status != "WAITING":
            raise ValueError("Only WAITING tickets can be called")
        self.status = "CALLED"
        self.log("Status -> CALLED")
        self.notify(f"Ticket {self.ticket_id} has been called!")

    def mark_done(self) -> None:
        if self.status not in ("WAITING", "CALLED"):
            raise ValueError("Ticket must be WAITING or CALLED to finish")
        self.status = "DONE"
        self.log("Status -> DONE")

    def cancel(self) -> None:
        if self.status in ("DONE", "CANCELED"):
            raise ValueError("Ticket already DONE/CANCELED")
        self.status = "CANCELED"
        self.log("Status -> CANCELED")

    def summary(self) -> str:
        t = self.created_at.strftime("%H:%M:%S")
        return f"{self.ticket_id} | P={self.priority} | {self.status} | {t}"

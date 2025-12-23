# Core/queue_system.py
from __future__ import annotations
from typing import Dict, List, Optional

from Core.person import Customer
from Core.service import Service
from Core.ticket import Ticket


class QueueSystem:
    def __init__(self) -> None:
        self.customers: Dict[str, Customer] = {}
        self.services: Dict[str, Service] = {}
        self.tickets: Dict[str, Ticket] = {}

        self.queues_by_service: Dict[str, List[str]] = {}  # service_id -> [ticket_id, ...]
        self._ticket_counter: int = 1000

    # ---- Customers ----
    def add_customer(self, customer: Customer) -> None:
        if customer.person_id in self.customers:
            raise ValueError("Customer already exists")
        self.customers[customer.person_id] = customer

    def get_customer(self, customer_id: str) -> Customer:
        if customer_id not in self.customers:
            raise KeyError("Customer not found")
        return self.customers[customer_id]

    # ---- Services ----
    def add_service(self, service: Service) -> None:
        if service.service_id in self.services:
            raise ValueError("Service already exists")
        self.services[service.service_id] = service
        self.queues_by_service[service.service_id] = []

    def list_services(self) -> List[Service]:
        return list(self.services.values())

    # ---- Tickets list (for admin) ----
    def list_tickets(self, status: Optional[str] = None) -> List[Ticket]:
        tickets = list(self.tickets.values())
        if status is None:
            return tickets
        return [t for t in tickets if t.status == status]

    # ---- Queue helpers (PRIORITY) ----
    def _enqueue_ticket(self, service_id: str, ticket_id: str) -> None:
        """
        מכניס טיקט לתור לפי עדיפות:
        priority=1 נכנס לפני priority=0 (ועדיין שומר FIFO בתוך אותה עדיפות).
        """
        q = self.queues_by_service[service_id]
        t = self.tickets[ticket_id]

        if t.priority == 0:
            q.append(ticket_id)
            return

        # priority=1: נכנס אחרי כל ה-priority=1 הקיימים (FIFO בתוך P=1)
        insert_idx = 0
        for i, tid in enumerate(q):
            if self.tickets[tid].priority == 1:
                insert_idx = i + 1
            else:
                break
        q.insert(insert_idx, ticket_id)

    def _reorder_waiting_ticket(self, ticket_id: str) -> None:
        """
        אם טיקט WAITING נמצא בתור, מסדר אותו מחדש לפי priority.
        """
        t = self.tickets[ticket_id]
        if t.status != "WAITING":
            return

        q = self.queues_by_service.get(t.service_id, [])
        if ticket_id not in q:
            return

        q.remove(ticket_id)
        self._enqueue_ticket(t.service_id, ticket_id)

    # ---- Tickets & Queue ----
    def create_ticket(self, customer_id: str, service_id: str, priority: Optional[int] = None) -> Ticket:
        if customer_id not in self.customers:
            raise KeyError("Customer not found")
        if service_id not in self.services:
            raise KeyError("Service not found")

        customer = self.customers[customer_id]
        if customer.is_waiting():
            raise ValueError("Customer already has an active ticket")

        self._ticket_counter += 1
        ticket_id = f"T{self._ticket_counter}"

        # אם לא הועבר priority, ניקח מהלקוח (או 0)
        p = customer.priority if priority is None else int(priority)

        ticket = Ticket(ticket_id=ticket_id, customer_id=customer_id, service_id=service_id, priority=p)
        self.tickets[ticket_id] = ticket

        self._enqueue_ticket(service_id, ticket_id)  # ✅ הכנסת תור לפי עדיפות
        customer.set_active_ticket(ticket_id)

        ticket.log("Added to queue")
        return ticket

    def set_ticket_priority(self, ticket_id: str, new_priority: int) -> None:
        """
        Admin: שינוי עדיפות לטיקט קיים (רק אם הוא WAITING),
        ואז סידור מחדש בתור.
        """
        if ticket_id not in self.tickets:
            raise KeyError("Ticket not found")
        t = self.tickets[ticket_id]
        t.set_priority(new_priority)
        self._reorder_waiting_ticket(ticket_id)
        t.log("Queue reordered after priority change")

    def peek_next_ticket(self, service_id: str) -> Optional[Ticket]:
        q = self.queues_by_service.get(service_id, [])
        if not q:
            return None
        return self.tickets[q[0]]

    def call_next_ticket(self, service_id: str) -> Optional[Ticket]:
        q = self.queues_by_service.get(service_id, [])
        if not q:
            return None

        ticket_id = q.pop(0)
        ticket = self.tickets[ticket_id]
        ticket.mark_called()

        # משחררים לקוח כדי שיוכל לפתוח טיקט נוסף אחרי שנקרא
        customer = self.customers[ticket.customer_id]
        if customer.active_ticket_id == ticket_id:
            customer.set_active_ticket(None)

        ticket.log("Customer released from queue on CALL")
        return ticket

    def finish_ticket(self, ticket_id: str) -> None:
        if ticket_id not in self.tickets:
            raise KeyError("Ticket not found")
        ticket = self.tickets[ticket_id]
        ticket.mark_done()

        customer = self.customers[ticket.customer_id]
        if customer.active_ticket_id == ticket_id:
            customer.set_active_ticket(None)

    def cancel_ticket(self, ticket_id: str) -> None:
        if ticket_id not in self.tickets:
            raise KeyError("Ticket not found")

        ticket = self.tickets[ticket_id]
        ticket.cancel()

        q = self.queues_by_service.get(ticket.service_id, [])
        if ticket_id in q:
            q.remove(ticket_id)

        customer = self.customers[ticket.customer_id]
        if customer.active_ticket_id == ticket_id:
            customer.set_active_ticket(None)

    def queue_length(self, service_id: str) -> int:
        return len(self.queues_by_service.get(service_id, []))

    def estimate_wait_minutes(self, service_id: str) -> int:
        if service_id not in self.services:
            raise KeyError("Service not found")
        return self.queue_length(service_id) * self.services[service_id].avg_minutes

# Core/queue_system.py
from __future__ import annotations
from typing import Dict, List, Optional

from Core.person import Customer
from Core.service import Service
from Core.ticket import Ticket


class QueueSystem:
    def __init__(self) -> None:
        # dict (דרישה)
        self.customers: Dict[str, Customer] = {}
        self.services: Dict[str, Service] = {}
        self.tickets: Dict[str, Ticket] = {}

        # dict + list (דרישה): תור לכל שירות
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

    # ---- Tickets & Queue ----
    def create_ticket(self, customer_id: str, service_id: str) -> Ticket:
        if customer_id not in self.customers:
            raise KeyError("Customer not found")
        if service_id not in self.services:
            raise KeyError("Service not found")

        customer = self.customers[customer_id]
        if customer.is_waiting():
            raise ValueError("Customer already has an active ticket")

        self._ticket_counter += 1
        ticket_id = f"T{self._ticket_counter}"

        ticket = Ticket(ticket_id=ticket_id, customer_id=customer_id, service_id=service_id)
        self.tickets[ticket_id] = ticket

        self.queues_by_service[service_id].append(ticket_id)  # list (דרישה)
        customer.set_active_ticket(ticket_id)

        ticket.log("Added to queue")
        return ticket

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

        # 🔧 תיקון הבאג:
        # הלקוח כבר לא "מחכה בתור" ולכן משחררים אותו
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

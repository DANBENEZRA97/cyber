# Core/person.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Person:
    person_id: str
    full_name: str
    phone: str

    def update_phone(self, new_phone: str) -> None:
        self.phone = new_phone

    def short_display(self) -> str:
        return f"{self.full_name} ({self.person_id})"


class Customer(Person):  
    def __init__(self, person_id: str, full_name: str, phone: str, priority: int = 0) -> None:
        super().__init__(person_id, full_name, phone)
        self.priority: int = priority             
        self.active_ticket_id: Optional[str] = None #
    def set_active_ticket(self, ticket_id: Optional[str]) -> None:
        self.active_ticket_id = ticket_id

    def is_waiting(self) -> bool:
        return self.active_ticket_id is not None

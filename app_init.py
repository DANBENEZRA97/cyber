from Core.queue_system import QueueSystem
from Core.person import Customer, PriorityCustomer
from Core.service import Service


def init_system() -> QueueSystem:
    system = QueueSystem()

    # Seed services
    system.add_service(Service("S1", "Customer Support", 7))
    system.add_service(Service("S2", "Payments", 5))
    system.add_service(Service("S3", "Tech Help", 10))

    # Seed customers
    vip = [
        PriorityCustomer(person_id="VIP1", full_name="VIP Client", phone="050-9999999")
    ]
    customers = [
        Customer("C1", "Alice Cohen", "050-1111111", priority=0),
        Customer("C2", "Bob Levi", "050-2222222", priority=1),
        Customer("C3", "Dana Israel", "050-3333333", priority=0),
        Customer("C4", "Eyal Mor", "050-4444444", priority=1),
        Customer("C5", "Noa Bar", "050-5555555", priority=0),
    ]

    for c in customers:
        system.add_customer(c)
    for v in vip:
        system.add_customer(v)

    # Seed tickets
    system.create_ticket("VIP1", "S1", priority=1)  # VIP ticket
    system.create_ticket("C1", "S1", priority=0)
    system.create_ticket("C2", "S1", priority=1)
    system.create_ticket("C3", "S1", priority=0)
    system.create_ticket("C4", "S1", priority=1)
    system.create_ticket("C5", "S2", priority=0)

    return system

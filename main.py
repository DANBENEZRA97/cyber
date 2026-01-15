from __future__ import annotations

from Core.queue_system import QueueSystem
from Core.service import Service
from Core.person import Customer, PriorityCustomer

from gui_app import run_gui


def run_demo() -> QueueSystem:
    """
    Demo: richer initialization + execution.
    Creates multiple services, VIP customers, priority customers, and tickets
    distributed across services. Runs core functions to demonstrate behavior.
    """
    print("=== DEMO START ===")

    system = QueueSystem()

    # ----------------------------
    # 1) Initialize services
    # ----------------------------
    services = [
        Service("S1", "Customer Support", 7),
        Service("S2", "Payments", 5),
        Service("S3", "Tech Help", 10),
    ]
    for s in services:
        system.add_service(s)

    print("\n[Init] Services created:")
    for s in services:
        print(f"- {s.service_id}: {s.name} (avg {s.avg_minutes} min)")

    # ----------------------------
    # 2) Initialize customers
    # ----------------------------
    # VIP customers (PriorityCustomer implies priority=1 and is_vip=True in your design)
    vip_customers = [
        PriorityCustomer("VIP1", "VIP Client 1", "050-9000001"),
        PriorityCustomer("VIP2", "VIP Client 2", "050-9000002"),
        PriorityCustomer("VIP3", "VIP Client 3", "050-9000003"),
    ]

    # Regular customers with priority=1
    pr1_customers = [
        Customer("P1_01", "Priority One 01", "050-8100001", priority=1),
        Customer("P1_02", "Priority One 02", "050-8100002", priority=1),
        Customer("P1_03", "Priority One 03", "050-8100003", priority=1),
        Customer("P1_04", "Priority One 04", "050-8100004", priority=1),
        Customer("P1_05", "Priority One 05", "050-8100005", priority=1),
    ]

    # Regular customers with priority=0
    pr0_customers = [
        Customer("P0_01", "Regular 01", "050-7000001", priority=0),
        Customer("P0_02", "Regular 02", "050-7000002", priority=0),
        Customer("P0_03", "Regular 03", "050-7000003", priority=0),
        Customer("P0_04", "Regular 04", "050-7000004", priority=0),
        Customer("P0_05", "Regular 05", "050-7000005", priority=0),
        Customer("P0_06", "Regular 06", "050-7000006", priority=0),
        Customer("P0_07", "Regular 07", "050-7000007", priority=0),
        Customer("P0_08", "Regular 08", "050-7000008", priority=0),
        Customer("P0_09", "Regular 09", "050-7000009", priority=0),
        Customer("P0_10", "Regular 10", "050-7000010", priority=0),
    ]

    for c in (vip_customers + pr1_customers + pr0_customers):
        system.add_customer(c)

    print("\n[Init] Customers created:")
    print(f"- VIP customers: {len(vip_customers)}")
    print(f"- Priority=1 customers: {len(pr1_customers)}")
    print(f"- Priority=0 customers: {len(pr0_customers)}")

    # ----------------------------
    # 3) Create tickets (distribution per service)
    # ----------------------------
    # Choose how many tickets per service
    tickets_plan = {
        "S1": {  # Customer Support
            "vip": ["VIP1", "VIP2"],
            "p1": ["P1_01", "P1_02"],
            "p0": ["P0_01", "P0_02", "P0_03", "P0_04", "P0_05"],
        },
        "S2": {  # Payments
            "vip": ["VIP3"],
            "p1": ["P1_03", "P1_04"],
            "p0": ["P0_06", "P0_07", "P0_08"],
        },
        "S3": {  # Tech Help
            "vip": [],
            "p1": ["P1_05"],
            "p0": ["P0_09", "P0_10"],
        },
    }

    created_ticket_ids: list[str] = []

    print("\n[Run] Creating tickets per service:")
    for service_id, group in tickets_plan.items():
        count = 0

        for cid in group["vip"]:
            t = system.create_ticket(cid, service_id, priority=1)
            created_ticket_ids.append(t.ticket_id)
            count += 1

        for cid in group["p1"]:
            t = system.create_ticket(cid, service_id, priority=1)
            created_ticket_ids.append(t.ticket_id)
            count += 1

        for cid in group["p0"]:
            t = system.create_ticket(cid, service_id, priority=0)
            created_ticket_ids.append(t.ticket_id)
            count += 1

        print(f"- {service_id}: {count} tickets")

    # ----------------------------
    # 4) Demonstrate core functions
    # ----------------------------
    print("\n[Run] Demonstrating core functions:")

    # 4.1 set_ticket_priority: take a waiting P0 ticket and upgrade to priority=1
    # Find one WAITING ticket that is currently priority=0
    upgraded_tid = None
    for tid in created_ticket_ids:
        if system.tickets[tid].status == "WAITING" and system.tickets[tid].priority == 0:
            upgraded_tid = tid
            break

    if upgraded_tid:
        system.set_ticket_priority(upgraded_tid, 1)
        print(f"- set_ticket_priority: upgraded {upgraded_tid} to P=1")

    # 4.2 call_next_ticket + finish_ticket: call and finish 2 tickets in S1
    for i in range(2):
        called = system.call_next_ticket("S1")
        print(f"- call_next_ticket(S1): called {called.ticket_id}")
        system.finish_ticket(called.ticket_id)
        print(f"  finish_ticket: finished {called.ticket_id}")

    # 4.3 cancel_ticket: cancel one waiting ticket in S2
    canceled_tid = None
    for tid in created_ticket_ids:
        t = system.tickets[tid]
        if t.service_id == "S2" and t.status == "WAITING":
            canceled_tid = tid
            break

    if canceled_tid:
        system.cancel_ticket(canceled_tid)
        print(f"- cancel_ticket: canceled {canceled_tid} (S2)")

    # 4.4 audit log example
    print("\n[Run] Audit log sample (last 5 lines):")
    sample_tid = created_ticket_ids[0]
    for line in system.tickets[sample_tid].get_audit_log()[-5:]:
        print("  -", line)

    print("\n=== DEMO END ===\n")
    return system



def main() -> None:
    system = run_demo()
    run_gui(system)


if __name__ == "__main__":
    main()

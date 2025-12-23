# gui_app.py
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox

from Core.queue_system import QueueSystem
from Core.person import Customer
from Core.service import Service


class QueueApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Queue Management System")
        self.geometry("900x520")

        # המערכת הלוגית (ה-Store/System של הפרויקט)
        self.system = QueueSystem()
        self._seed_data()

        self._build_ui()
        self._refresh_queue_list()

    def _seed_data(self) -> None:
        # שירותים התחלתיים
        self.system.add_service(Service("S1", "Customer Support", 7))
        self.system.add_service(Service("S2", "Payments", 5))
        self.system.add_service(Service("S3", "Tech Help", 10))

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        # אזור עליון: יצירת לקוח+טיקט
        top = ttk.LabelFrame(self, text="Create Ticket")
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Customer ID:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.ent_customer_id = ttk.Entry(top, width=20)
        self.ent_customer_id.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(top, text="Full Name:").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.ent_full_name = ttk.Entry(top, width=25)
        self.ent_full_name.grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(top, text="Phone:").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.ent_phone = ttk.Entry(top, width=20)
        self.ent_phone.grid(row=0, column=5, padx=6, pady=6)

        ttk.Label(top, text="Service:").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.cmb_service = ttk.Combobox(top, state="readonly", width=27)
        self.cmb_service.grid(row=1, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(top, text="Priority (0/1):").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        self.ent_priority = ttk.Entry(top, width=10)
        self.ent_priority.grid(row=1, column=3, padx=6, pady=6, sticky="w")
        self.ent_priority.insert(0, "0")

        self.btn_create = ttk.Button(top, text="Create Ticket", command=self.on_create_ticket)  # Event 1
        self.btn_create.grid(row=1, column=5, padx=6, pady=6, sticky="e")

        # למלא שירותים בקומבו
        services = self.system.list_services()
        self.service_display_to_id = {s.display(): s.service_id for s in services}  # dict
        self.cmb_service["values"] = list(self.service_display_to_id.keys())
        if services:
            self.cmb_service.current(0)

        # אזור אמצעי: תור + פעולות
        mid = ttk.Frame(self)
        mid.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.LabelFrame(mid, text="Queue (by service)")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ttk.Label(left, text="Choose service:").pack(anchor="w", padx=8, pady=(8, 4))
        self.cmb_service_queue = ttk.Combobox(left, state="readonly")
        self.cmb_service_queue.pack(fill="x", padx=8)
        self.cmb_service_queue["values"] = list(self.service_display_to_id.keys())
        self.cmb_service_queue.bind("<<ComboboxSelected>>", lambda e: self._refresh_queue_list())  # Event (שינוי בחירה)
        self.cmb_service_queue.current(0)

        self.lst_queue = tk.Listbox(left, height=15)
        self.lst_queue.pack(fill="both", expand=True, padx=8, pady=8)

        # Event 3: דאבל קליק להצגת Audit Log
        self.lst_queue.bind("<Double-Button-1>", self.on_ticket_double_click)

        btns = ttk.Frame(left)
        btns.pack(fill="x", padx=8, pady=(0, 8))

        self.btn_call_next = ttk.Button(btns, text="Call Next", command=self.on_call_next)  # Event 2
        self.btn_call_next.pack(side="left")

        self.btn_finish = ttk.Button(btns, text="Finish Selected", command=self.on_finish_selected)
        self.btn_finish.pack(side="left", padx=6)

        self.btn_cancel = ttk.Button(btns, text="Cancel Selected", command=self.on_cancel_selected)
        self.btn_cancel.pack(side="left")

        # אזור ימני: Audit/Info
        right = ttk.LabelFrame(mid, text="Ticket Details / Audit Log")
        right.pack(side="left", fill="both", expand=True)

        self.txt_details = tk.Text(right, height=20, wrap="word")
        self.txt_details.pack(fill="both", expand=True, padx=8, pady=8)

    # ---------------- Events / Handlers ----------------
    def on_create_ticket(self) -> None:
        try:
            customer_id = self.ent_customer_id.get().strip()
            full_name = self.ent_full_name.get().strip()
            phone = self.ent_phone.get().strip()
            priority_str = self.ent_priority.get().strip()

            if not customer_id or not full_name or not phone:
                raise ValueError("Please fill Customer ID, Full Name, Phone")

            priority = int(priority_str)
            if priority not in (0, 1):
                raise ValueError("Priority must be 0 or 1")

            service_display = self.cmb_service.get()
            service_id = self.service_display_to_id[service_display]

            # אם הלקוח לא קיים – ניצור אותו
            if customer_id not in self.system.customers:
                self.system.add_customer(Customer(customer_id, full_name, phone, priority=priority))
            else:
                # אם קיים, נעדכן שם/טלפון/עדיפות (פשוט)
                c = self.system.customers[customer_id]
                c.full_name = full_name
                c.update_phone(phone)
                c.priority = priority

            ticket = self.system.create_ticket(customer_id, service_id)
            messagebox.showinfo("Success", f"Created {ticket.ticket_id}")
            self._refresh_queue_list()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_call_next(self) -> None:
        try:
            service_id = self._selected_queue_service_id()
            ticket = self.system.call_next_ticket(service_id)
            if not ticket:
                messagebox.showinfo("Info", "Queue is empty.")
                return
            self._refresh_queue_list()
            self._show_ticket_details(ticket.ticket_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_finish_selected(self) -> None:
        ticket_id = self._selected_ticket_id()
        if not ticket_id:
            return
        try:
            self.system.finish_ticket(ticket_id)
            self._refresh_queue_list()
            self._show_text(f"Finished {ticket_id}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_cancel_selected(self) -> None:
        ticket_id = self._selected_ticket_id()
        if not ticket_id:
            return
        try:
            self.system.cancel_ticket(ticket_id)
            self._refresh_queue_list()
            self._show_text(f"Canceled {ticket_id}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_ticket_double_click(self, _event) -> None:
        ticket_id = self._selected_ticket_id()
        if ticket_id:
            self._show_ticket_details(ticket_id)

    # ---------------- Helpers ----------------
    def _selected_queue_service_id(self) -> str:
        display = self.cmb_service_queue.get()
        return self.service_display_to_id[display]

    def _refresh_queue_list(self) -> None:
        self.lst_queue.delete(0, tk.END)

        service_id = self._selected_queue_service_id()
        ticket_ids = self.system.queues_by_service.get(service_id, [])

        for tid in ticket_ids:
            t = self.system.tickets[tid]
            self.lst_queue.insert(tk.END, t.summary())

        est = self.system.estimate_wait_minutes(service_id)
        self._show_text(f"Service queue refreshed. Estimated wait: {est} minutes.\n")

    def _selected_ticket_id(self):
        selection = self.lst_queue.curselection()
        if not selection:
            messagebox.showinfo("Info", "Select a ticket from the list.")
            return None
        line = self.lst_queue.get(selection[0])
        # summary: "T1001 | WAITING | 12:34:56"
        return line.split("|")[0].strip()

    def _show_ticket_details(self, ticket_id: str) -> None:
        t = self.system.tickets[ticket_id]
        c = self.system.customers.get(t.customer_id)
        s = self.system.services.get(t.service_id)

        text = []
        text.append(f"Ticket: {t.ticket_id}")
        text.append(f"Status: {t.status}")
        text.append(f"Customer: {c.short_display() if c else t.customer_id}")
        text.append(f"Service: {s.display() if s else t.service_id}")
        text.append("\n--- Audit Log ---")
        for row in t.get_audit_log():
            text.append(row)

        self.txt_details.delete("1.0", tk.END)
        self.txt_details.insert(tk.END, "\n".join(text))

    def _show_text(self, msg: str) -> None:
        self.txt_details.insert(tk.END, msg)
        self.txt_details.see(tk.END)


def run_gui() -> None:
    app = QueueApp()
    app.mainloop()

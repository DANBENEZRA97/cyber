from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog  # 🔐 NEW

from Core.queue_system import QueueSystem
from Core.person import Customer, PriorityCustomer
from Core.service import Service

ADMIN_PASSWORD = "admin123"  # 🔐 NEW


class QueueApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Queue Management System")
        self.geometry("950x600")

        self.system = QueueSystem()
        self._seed_data()

        self.admin_authenticated = False  # 🔐 NEW

        self._build_ui()
        self._refresh_user_queue()
        self._refresh_admin_list()

    def _seed_data(self) -> None:
        # Seed some services
        self.system.add_service(Service("S1", "Customer Support", 7))
        self.system.add_service(Service("S2", "Payments", 5))
        self.system.add_service(Service("S3", "Tech Help", 10))

        # Seed some customers
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
            self.system.add_customer(c)
        for v in vip:
            self.system.add_customer(v)

        self.system.create_ticket("VIP1", "S1", priority=1) # VIP ticket
        self.system.create_ticket("C1", "S1", priority=0)
        self.system.create_ticket("C2", "S1", priority=1)
        self.system.create_ticket("C3", "S1", priority=0)
        self.system.create_ticket("C4", "S1", priority=1)
        self.system.create_ticket("C5", "S2", priority=0)

    def _build_ui(self) -> None:
        services = self.system.list_services()
        self.service_display_to_id = {s.display(): s.service_id for s in services}
        service_values = list(self.service_display_to_id.keys())

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)  # 🔐 NEW
        self.notebook = notebook  # 🔐 NEW (רק שמירה לרפרנס)

        self.tab_user = ttk.Frame(notebook)
        self.tab_admin = ttk.Frame(notebook)

        notebook.add(self.tab_user, text="User")
        notebook.add(self.tab_admin, text="Admin")

        # ================= USER TAB =================
        user_top = ttk.LabelFrame(self.tab_user, text="Enter Queue")
        user_top.pack(fill="x", padx=10, pady=10)

        ttk.Label(user_top, text="Customer ID:").grid(row=0, column=0, padx=6, pady=6)
        self.u_id = ttk.Entry(user_top, width=22)
        self.u_id.grid(row=0, column=1, padx=6)

        ttk.Label(user_top, text="Full Name:").grid(row=0, column=2, padx=6)
        self.u_name = ttk.Entry(user_top, width=26)
        self.u_name.grid(row=0, column=3, padx=6)

        ttk.Label(user_top, text="Phone:").grid(row=0, column=4, padx=6)
        self.u_phone = ttk.Entry(user_top, width=18)
        self.u_phone.grid(row=0, column=5, padx=6)

        ttk.Label(user_top, text="Service:").grid(row=1, column=0, padx=6)
        self.u_service = ttk.Combobox(user_top, state="readonly", values=service_values)
        self.u_service.grid(row=1, column=1, padx=6)
        if service_values:
            self.u_service.current(0)

        self.u_service.bind("<<ComboboxSelected>>", lambda e: self._refresh_user_queue())

        ttk.Button(user_top, text="Join Queue", command=self.on_user_join).grid(
            row=1, column=5, padx=6, pady=6
        )

        user_mid = ttk.Frame(self.tab_user)
        user_mid.pack(fill="both", expand=True, padx=10, pady=10)

        self.user_queue = tk.Listbox(user_mid, height=18)
        self.user_queue.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.user_output = tk.Text(user_mid, wrap="word")
        self.user_output.pack(side="left", fill="both", expand=True)

        # ================= ADMIN TAB =================
        admin_top = ttk.LabelFrame(self.tab_admin, text="Admin Control")
        admin_top.pack(fill="x", padx=10, pady=10)

        ttk.Label(admin_top, text="Customer ID:").grid(row=0, column=0, padx=6)
        self.a_id = ttk.Entry(admin_top, width=20)
        self.a_id.grid(row=0, column=1, padx=6)

        ttk.Label(admin_top, text="Full Name:").grid(row=0, column=2, padx=6)
        self.a_name = ttk.Entry(admin_top, width=24)
        self.a_name.grid(row=0, column=3, padx=6)

        ttk.Label(admin_top, text="Phone:").grid(row=0, column=4, padx=6)
        self.a_phone = ttk.Entry(admin_top, width=18)
        self.a_phone.grid(row=0, column=5, padx=6)

        ttk.Label(admin_top, text="Service (filter + actions):").grid(row=1, column=0, padx=6)
        self.a_service = ttk.Combobox(admin_top, state="readonly", values=service_values)
        self.a_service.grid(row=1, column=1, padx=6)
        if service_values:
            self.a_service.current(0)

        self.a_service.bind(
            "<<ComboboxSelected>>",
            lambda e: (self._refresh_admin_list(), self._refresh_user_queue())
        )

        ttk.Label(admin_top, text="Priority (0/1):").grid(row=1, column=2, padx=6)
        self.a_priority = ttk.Entry(admin_top, width=10)
        self.a_priority.grid(row=1, column=3, padx=6)
        self.a_priority.insert(0, "0")

        ttk.Button(admin_top, text="Create Ticket", command=self.on_admin_create).grid(
            row=1, column=5, padx=6
        )

        admin_mid = ttk.Frame(self.tab_admin)
        admin_mid.pack(fill="both", expand=True, padx=10, pady=10)

        self.admin_list = tk.Listbox(admin_mid, height=18)
        self.admin_list.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.admin_list.bind("<Double-Button-1>", self.on_admin_select)

        admin_controls = ttk.Frame(admin_mid)
        admin_controls.pack(side="left", fill="y")

        ttk.Button(admin_controls, text="Call Next", command=self.on_call_next).pack(fill="x", pady=4)
        ttk.Button(admin_controls, text="Finish", command=self.on_finish).pack(fill="x", pady=4)
        ttk.Button(admin_controls, text="Cancel", command=self.on_cancel).pack(fill="x", pady=4)

        ttk.Separator(admin_controls, orient="horizontal").pack(fill="x", pady=10)

        ttk.Label(admin_controls, text="Change Priority of selected ticket:").pack(anchor="w", pady=(0, 4))
        self.adm_new_priority = ttk.Combobox(admin_controls, state="readonly", values=["0", "1"], width=6)
        self.adm_new_priority.pack(anchor="w")
        self.adm_new_priority.current(0)

        ttk.Button(admin_controls, text="Set Priority", command=self.on_set_priority).pack(fill="x", pady=6)

        self.admin_details = tk.Text(admin_mid, wrap="word")
        self.admin_details.pack(side="left", fill="both", expand=True)

    # 🔐 Check for the admin Password
    def _on_tab_change(self, event):
        selected = event.widget.tab(event.widget.index("current"))["text"]
        if selected == "Admin" and not self.admin_authenticated:
            pwd = simpledialog.askstring("Admin Login", "Enter admin password:", show="*")
            if pwd != ADMIN_PASSWORD:
                messagebox.showerror("Access Denied", "Wrong password")
                event.widget.select(0)  # חזרה ל-User
            else:
                self.admin_authenticated = True
                messagebox.showinfo("Success", "Admin access granted")

    # ================= USER =================
    def on_user_join(self) -> None:
        try:
            cid = self.u_id.get().strip()
            name = self.u_name.get().strip()
            phone = self.u_phone.get().strip()
            if not cid or not name or not phone:
                raise ValueError("Fill all fields")

            service_id = self.service_display_to_id[self.u_service.get()]

            if cid not in self.system.customers:
                self.system.add_customer(Customer(cid, name, phone, priority=0)) # New customers are normal priority
            else: 
                c = self.system.customers[cid] 
                c.full_name, c.phone, c.priority = name, phone, 0

            ticket = self.system.create_ticket(cid, service_id, priority=0)

            self.user_output.delete("1.0", tk.END)
            self.user_output.insert(tk.END, f"Hello {name}\nYour ticket number is {ticket.ticket_id}")

            self._refresh_user_queue()
            self._refresh_admin_list()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= ADMIN =================
    def on_admin_create(self) -> None:
        try:
            cid = self.a_id.get().strip()
            name = self.a_name.get().strip()
            phone = self.a_phone.get().strip()
            if not cid or not name or not phone:
                raise ValueError("Fill all fields")

            priority = int(self.a_priority.get().strip())
            if priority not in (0, 1):
                raise ValueError("Priority must be 0 or 1")

            service_id = self.service_display_to_id[self.a_service.get()]

            if cid not in self.system.customers:
                self.system.add_customer(Customer(cid, name, phone, priority))
            else:
                c = self.system.customers[cid]
                c.full_name, c.phone, c.priority = name, phone, priority

            self.system.create_ticket(cid, service_id, priority=priority)
            self._refresh_user_queue()
            self._refresh_admin_list()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_call_next(self):
        try:
            service_id = self.service_display_to_id[self.a_service.get()]
            self.system.call_next_ticket(service_id)
            self._refresh_user_queue()
            self._refresh_admin_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_finish(self):
        try:
            tid = self._selected_admin_ticket()
            if tid:
                self.system.finish_ticket(tid)
                self._refresh_admin_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_cancel(self):
        try:
            tid = self._selected_admin_ticket()
            if tid:
                self.system.cancel_ticket(tid)
                self._refresh_admin_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_set_priority(self):
        try:
            tid = self._selected_admin_ticket()
            if not tid:
                return
            new_p = int(self.adm_new_priority.get())
            self.system.set_ticket_priority(tid, new_p)
            self._refresh_user_queue()
            self._refresh_admin_list()
            self._show_admin_details(tid)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_admin_select(self, _):
        tid = self._selected_admin_ticket()
        if tid:
            self._show_admin_details(tid)

    # ================= HELPERS =================
    def _refresh_user_queue(self):
        self.user_queue.delete(0, tk.END)
        if not self.u_service.get():
            return

        service_id = self.service_display_to_id[self.u_service.get()]
        q = self.system.queues_by_service.get(service_id, [])
        for tid in q:
            t = self.system.tickets[tid]
            name = self.system.customers[t.customer_id].full_name
            self.user_queue.insert(tk.END, name)

    def _refresh_admin_list(self):
        self.admin_list.delete(0, tk.END)
        if not self.a_service.get():
            return

        service_id = self.service_display_to_id[self.a_service.get()]
        tickets = [t for t in self.system.tickets.values() if t.service_id == service_id]
        tickets.sort(key=lambda x: x.created_at)

        for t in tickets:
            c = self.system.customers.get(t.customer_id)
            name = c.full_name if c else "UNKNOWN"
            self.admin_list.insert(tk.END, f"{t.ticket_id} | P={t.priority} | {t.status} | {name}")

    def _selected_admin_ticket(self):
        sel = self.admin_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a ticket from the admin list.")
            return None
        return self.admin_list.get(sel[0]).split("|")[0].strip()

    def _show_admin_details(self, tid: str):
        t = self.system.tickets[tid]
        c = self.system.customers.get(t.customer_id)
        s = self.system.services.get(t.service_id)

        self.admin_details.delete("1.0", tk.END)
        self.admin_details.insert(
            tk.END,
            f"Ticket: {t.ticket_id}\n"
            f"Status: {t.status}\n"
            f"Priority: {t.priority}\n"
            f"Service: {s.name if s else t.service_id}\n\n"
            f"Customer ID: {c.person_id if c else 'UNKNOWN'}\n"
            f"Full Name: {c.full_name if c else 'UNKNOWN'}\n"
            f"Phone: {c.phone if c else 'UNKNOWN'}\n\n"
            f"Audit:\n" + "\n".join(t.get_audit_log())
        )


def run_gui():
    QueueApp().mainloop()

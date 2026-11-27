import tkinter as tk
from tkinter import ttk, messagebox

from domain import (
    Actor,
    ClaimTicket,
    ConversationPolicy,
    MemoryTicketRepository,
    Priority,
    Role,
    RuleViolation,
    Status,
    SupportTicket,
    Urgency,
)


class FixItGUI:
    """Presentation-layer adapter for the FixIt DDD Python prototype."""

    COLORS = {
        "navy": "#142B40",
        "teal": "#0D9488",
        "teal_dark": "#0F766E",
        "bg": "#F1F5F9",
        "white": "#FFFFFF",
        "text": "#1E293B",
        "muted": "#64748B",
        "border": "#CBD5E1",
        "success": "#15803D",
        "success_bg": "#DCFCE7",
        "error": "#B91C1C",
        "error_bg": "#FEE2E2",
        "warning": "#B45309",
        "warning_bg": "#FEF3C7",
    }

    STATUS_COLORS = {
        "OPEN": "#0D9488",
        "ASSIGNED": "#2563EB",
        "IN_PROGRESS": "#B45309",
        "RESOLVED": "#15803D",
        "CLOSED": "#475569",
        "CANCELLED": "#B91C1C",
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FixIt — DDD Interactive Prototype")
        self.root.geometry("1220x840")
        self.root.minsize(1020, 740)
        self.root.configure(bg=self.COLORS["bg"])

        self.repository = MemoryTicketRepository()
        self.active_ticket_id = None
        self.ticket_metadata = {}  # Presentation-only storage for title/desc/category
        self.is_demo_running = False

        self.create_actors()
        self.configure_styles()
        self.build_interface()
        self.refresh_all()

    # ------------------------------------------------------------------
    # Setup & Styling
    # ------------------------------------------------------------------
    def create_actors(self):
        self.actors = {
            "Reporter": Actor("reporter-01", Role.REPORTER),
            "Support Agent A": Actor("agent-01", Role.SUPPORT_AGENT),
            "Support Agent B": Actor("agent-02", Role.SUPPORT_AGENT),
            "Administrator": Actor("admin-01", Role.ADMIN),
        }
        self.agent_actors = {
            "Support Agent A (agent-01)": self.actors["Support Agent A"],
            "Support Agent B (agent-02)": self.actors["Support Agent B"],
        }

    def configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Main.TFrame", background=self.COLORS["bg"])
        style.configure("Card.TFrame", background=self.COLORS["white"], relief="flat")
        style.configure(
            "CardTitle.TLabel",
            background=self.COLORS["white"],
            foreground=self.COLORS["navy"],
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "FieldLabel.TLabel",
            background=self.COLORS["white"],
            foreground=self.COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Value.TLabel",
            background=self.COLORS["white"],
            foreground=self.COLORS["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Primary.TButton",
            background=self.COLORS["teal"],
            foreground=self.COLORS["white"],
            font=("Segoe UI", 9, "bold"),
            padding=(10, 6),
        )
        style.map(
            "Primary.TButton",
            background=[("active", self.COLORS["teal_dark"]), ("disabled", "#94A3B8")],
        )
        style.configure(
            "Dark.TButton",
            background=self.COLORS["navy"],
            foreground=self.COLORS["white"],
            font=("Segoe UI", 9, "bold"),
            padding=(10, 6),
        )
        style.map(
            "Dark.TButton",
            background=[("active", "#1E3A5F"), ("disabled", "#94A3B8")],
        )
        style.configure(
            "Action.TButton",
            background="#E2E8F0",
            foreground=self.COLORS["text"],
            font=("Segoe UI", 9),
            padding=(8, 5),
        )
        style.map(
            "Action.TButton",
            background=[("active", "#CBD5E1"), ("disabled", "#F1F5F9")],
        )
        style.configure(
            "Treeview",
            background=self.COLORS["white"],
            fieldbackground=self.COLORS["white"],
            foreground=self.COLORS["text"],
            rowheight=24,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background="#E2E8F0",
            foreground=self.COLORS["navy"],
            font=("Segoe UI", 9, "bold"),
        )

    # ------------------------------------------------------------------
    # Interface Layout
    # ------------------------------------------------------------------
    def build_interface(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.build_header()

        container = ttk.Frame(self.root, style="Main.TFrame", padding=12)
        container.grid(row=1, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(3, weight=1)

        self.build_ticket_form(container)
        self.build_ticket_details(container)
        self.build_operations_panel(container)
        self.build_demo_and_feedback_panel(container)
        self.build_event_history(container)
        self.build_footer()

    def build_header(self):
        header = tk.Frame(self.root, bg=self.COLORS["navy"], padx=18, pady=12)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        left = tk.Frame(header, bg=self.COLORS["navy"])
        left.grid(row=0, column=0, sticky="w")
        tk.Label(
            left,
            text="FixIt",
            bg=self.COLORS["navy"],
            fg=self.COLORS["white"],
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            left,
            text="DDD Interactive Prototype",
            bg=self.COLORS["navy"],
            fg="#CBD5E1",
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        right = tk.Frame(header, bg=self.COLORS["navy"])
        right.grid(row=0, column=1, sticky="e")
        tk.Label(
            right,
            text="Software Engineering II",
            bg=self.COLORS["navy"],
            fg=self.COLORS["white"],
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="e")
        tk.Label(
            right,
            text="Keiser University Latin American Campus",
            bg=self.COLORS["navy"],
            fg="#CBD5E1",
            font=("Segoe UI", 9),
        ).pack(anchor="e")

    def build_ticket_form(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 10))
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Create Support Ticket (as Reporter)", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        ttk.Label(card, text="Ticket Title", style="FieldLabel.TLabel").grid(row=1, column=0, sticky="w")
        self.title_var = tk.StringVar(value="Wi-Fi connection problem")
        self.title_entry = ttk.Entry(card, textvariable=self.title_var)
        self.title_entry.grid(row=2, column=0, sticky="ew", pady=(2, 8))

        ttk.Label(card, text="Description", style="FieldLabel.TLabel").grid(row=3, column=0, sticky="w")
        self.desc_text = tk.Text(
            card, height=3, font=("Segoe UI", 9), relief="solid", borderwidth=1, wrap="word"
        )
        self.desc_text.insert("1.0", "Cannot connect to the university network.")
        self.desc_text.grid(row=4, column=0, sticky="ew", pady=(2, 8))

        row_frame = ttk.Frame(card, style="Card.TFrame")
        row_frame.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        row_frame.columnconfigure(0, weight=1)
        row_frame.columnconfigure(1, weight=1)

        ttk.Label(row_frame, text="Category", style="FieldLabel.TLabel").grid(row=0, column=0, sticky="w")
        self.category_var = tk.StringVar(value="Network")
        self.category_combo = ttk.Combobox(
            row_frame,
            textvariable=self.category_var,
            values=["Network", "Hardware", "Software", "Account", "Peripheral", "Other"],
        )
        self.category_combo.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(2, 0))

        ttk.Label(row_frame, text="Reporter Urgency", style="FieldLabel.TLabel").grid(row=0, column=1, sticky="w")
        self.urgency_var = tk.StringVar(value=Urgency.HIGH.name)
        self.urgency_combo = ttk.Combobox(
            row_frame,
            textvariable=self.urgency_var,
            values=[u.name for u in Urgency],
            state="readonly",
        )
        self.urgency_combo.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(2, 0))

        self.create_btn = ttk.Button(
            card, text="Create Ticket", style="Primary.TButton", command=self.create_ticket
        )
        self.create_btn.grid(row=6, column=0, sticky="ew")

    def build_ticket_details(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        card.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 10))
        card.columnconfigure(1, weight=1)
        card.columnconfigure(3, weight=1)

        ttk.Label(card, text="Current Ticket Information", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 8)
        )

        self.detail_vars = {
            "id": tk.StringVar(value="—"),
            "title": tk.StringVar(value="—"),
            "category": tk.StringVar(value="—"),
            "description": tk.StringVar(value="—"),
            "reporter": tk.StringVar(value="—"),
            "assignee": tk.StringVar(value="Not assigned"),
            "urgency": tk.StringVar(value="—"),
            "priority": tk.StringVar(value="Not assigned"),
            "version": tk.StringVar(value="—"),
            "chat_access": tk.StringVar(value="—"),
        }

        ttk.Label(card, text="Status:", style="FieldLabel.TLabel").grid(row=1, column=0, sticky="w", pady=2)
        self.status_label = tk.Label(
            card,
            text="NO ACTIVE TICKET",
            bg=self.COLORS["white"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 11, "bold"),
        )
        self.status_label.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(card, text="Version:", style="FieldLabel.TLabel").grid(row=1, column=2, sticky="w", padx=(10, 4))
        ttk.Label(card, textvariable=self.detail_vars["version"], style="Value.TLabel").grid(row=1, column=3, sticky="w")

        fields = [
            ("Ticket ID:", "id", "Category:", "category"),
            ("Title:", "title", "Reporter:", "reporter"),
            ("Urgency:", "urgency", "Assigned Agent:", "assignee"),
            ("Official Priority:", "priority", "Chat Access:", "chat_access"),
        ]

        for idx, (l1, k1, l2, k2) in enumerate(fields, start=2):
            ttk.Label(card, text=l1, style="FieldLabel.TLabel").grid(row=idx, column=0, sticky="w", pady=2)
            ttk.Label(card, textvariable=self.detail_vars[k1], style="Value.TLabel").grid(
                row=idx, column=1, sticky="w", padx=(4, 10), pady=2
            )
            ttk.Label(card, text=l2, style="FieldLabel.TLabel").grid(row=idx, column=2, sticky="w", padx=(10, 4), pady=2)
            ttk.Label(card, textvariable=self.detail_vars[k2], style="Value.TLabel").grid(
                row=idx, column=3, sticky="w", pady=2
            )

        ttk.Label(card, text="Description:", style="FieldLabel.TLabel").grid(row=6, column=0, sticky="nw", pady=2)
        ttk.Label(
            card, textvariable=self.detail_vars["description"], style="Value.TLabel", wraplength=420
        ).grid(row=6, column=1, columnspan=3, sticky="w", padx=(4, 0), pady=2)

        # Simulated Actor Selection
        sep = ttk.Separator(card, orient="horizontal")
        sep.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(10, 8))

        ttk.Label(
            card, text="Perform Operation As (Simulated Role — Not Real Auth):", style="FieldLabel.TLabel"
        ).grid(row=8, column=0, columnspan=2, sticky="w")
        self.actor_var = tk.StringVar(value="Support Agent A")
        self.actor_combo = ttk.Combobox(
            card,
            textvariable=self.actor_var,
            values=list(self.actors.keys()),
            state="readonly",
        )
        self.actor_combo.grid(row=8, column=2, columnspan=2, sticky="ew", padx=(8, 0))
        self.actor_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh_ticket_details())

    def build_operations_panel(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        for col in range(6):
            card.columnconfigure(col, weight=1)

        ttk.Label(card, text="Ticket Operations", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 8)
        )

        # Row 1: Core lifecycle buttons
        self.btn_claim = ttk.Button(card, text="Claim Ticket", style="Action.TButton", command=self.claim_ticket)
        self.btn_start = ttk.Button(card, text="Start Work", style="Action.TButton", command=self.start_work)
        self.btn_resolve = ttk.Button(card, text="Resolve Ticket", style="Action.TButton", command=self.resolve_ticket)
        self.btn_close = ttk.Button(card, text="Close Ticket", style="Action.TButton", command=self.close_ticket)
        self.btn_cancel = ttk.Button(card, text="Cancel Ticket", style="Action.TButton", command=self.cancel_ticket)
        self.btn_chat = ttk.Button(card, text="Check Chat Access", style="Action.TButton", command=self.check_chat_access)

        for i, btn in enumerate(
            [self.btn_claim, self.btn_start, self.btn_resolve, self.btn_close, self.btn_cancel, self.btn_chat]
        ):
            btn.grid(row=1, column=i, sticky="ew", padx=3, pady=(0, 8))

        # Row 2: Priority controls + Reassign controls + Reset
        self.priority_var = tk.StringVar(value=Priority.P2_HIGH.name)
        self.priority_combo = ttk.Combobox(
            card, textvariable=self.priority_var, values=[p.name for p in Priority], state="readonly", width=14
        )
        self.priority_combo.grid(row=2, column=0, sticky="ew", padx=3)

        self.reason_var = tk.StringVar(value="")
        self.reason_entry = ttk.Entry(card, textvariable=self.reason_var)
        self.reason_entry.grid(row=2, column=1, sticky="ew", padx=3)
        self.reason_entry.insert(0, "Optional reason...")
        self.reason_entry.bind("<FocusIn>", self._clear_reason_placeholder)

        self.btn_priority = ttk.Button(card, text="Set Priority", style="Action.TButton", command=self.set_priority)
        self.btn_priority.grid(row=2, column=2, sticky="ew", padx=3)

        self.reassign_var = tk.StringVar(value="Support Agent B (agent-02)")
        self.reassign_combo = ttk.Combobox(
            card, textvariable=self.reassign_var, values=list(self.agent_actors.keys()), state="readonly"
        )
        self.reassign_combo.grid(row=2, column=3, sticky="ew", padx=3)

        self.btn_reassign = ttk.Button(card, text="Reassign Agent", style="Action.TButton", command=self.reassign_agent)
        self.btn_reassign.grid(row=2, column=4, sticky="ew", padx=3)

        self.btn_reset = ttk.Button(card, text="Reset Demo", style="Dark.TButton", command=self.reset_demo)
        self.btn_reset.grid(row=2, column=5, sticky="ew", padx=3)

        self.operation_buttons = [
            self.btn_claim,
            self.btn_start,
            self.btn_resolve,
            self.btn_close,
            self.btn_cancel,
            self.btn_chat,
            self.btn_priority,
            self.btn_reassign,
        ]

    def build_demo_and_feedback_panel(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Demonstration Scenarios & Operation Feedback", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        self.btn_valid_demo = ttk.Button(
            card, text="Run Valid Lifecycle", style="Primary.TButton", command=self.run_valid_demo
        )
        self.btn_valid_demo.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(0, 8))

        self.btn_invalid_demo = ttk.Button(
            card, text="Run Invalid Operation", style="Dark.TButton", command=self.run_invalid_demo
        )
        self.btn_invalid_demo.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(0, 8))

        self.feedback_frame = tk.Frame(card, bg=self.COLORS["bg"], padx=10, pady=8)
        self.feedback_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.feedback_label = tk.Label(
            self.feedback_frame,
            text="Ready. Create a ticket manually or run one of the automated demonstration scenarios.",
            bg=self.COLORS["bg"],
            fg=self.COLORS["text"],
            font=("Segoe UI", 9, "bold"),
            justify="left",
            anchor="w",
        )
        self.feedback_label.pack(fill="x")

    def build_event_history(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.grid(row=3, column=0, columnspan=2, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        ttk.Label(card, text="Domain Event History (Immutable Aggregate Events)", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )

        columns = ("version", "kind", "actor", "before", "after", "reason", "timestamp")
        self.event_tree = ttk.Treeview(card, columns=columns, show="headings", height=6)

        headings = [
            ("version", "Version", 70),
            ("kind", "Event Type", 140),
            ("actor", "Actor", 110),
            ("before", "Before", 110),
            ("after", "After", 110),
            ("reason", "Reason", 220),
            ("timestamp", "Timestamp", 180),
        ]
        for col, text, width in headings:
            self.event_tree.heading(col, text=text)
            self.event_tree.column(col, width=width, anchor="w")

        vsb = ttk.Scrollbar(card, orient="vertical", command=self.event_tree.yview)
        hsb = ttk.Scrollbar(card, orient="horizontal", command=self.event_tree.xview)
        self.event_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.event_tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        hsb.grid(row=2, column=0, sticky="ew")

    def build_footer(self):
        footer = tk.Label(
            self.root,
            text="Academic DDD Prototype · In-memory persistence · Keiser University LAC",
            bg=self.COLORS["bg"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 8),
            pady=6,
        )
        footer.grid(row=2, column=0, sticky="ew")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _clear_reason_placeholder(self, _event=None):
        if self.reason_var.get() == "Optional reason...":
            self.reason_var.set("")

    def _enum_text(self, value, default="Not assigned"):
        if value is None:
            return default
        return getattr(value, "name", str(value))

    def get_selected_actor(self) -> Actor:
        return self.actors[self.actor_var.get()]

    def get_active_ticket(self):
        if self.active_ticket_id is None:
            return None
        return self.repository.get(self.active_ticket_id)

    def show_success(self, message: str):
        ticket = self.get_active_ticket()
        suffix = ""
        if ticket is not None:
            suffix = f"\nCurrent status: {self._enum_text(ticket.status)}  |  Aggregate version: {ticket.version}"
        self.feedback_frame.configure(bg=self.COLORS["success_bg"])
        self.feedback_label.configure(
            text=f"SUCCESS: {message}{suffix}",
            bg=self.COLORS["success_bg"],
            fg=self.COLORS["success"],
        )

    def show_error(self, message: str, extra_note: str = ""):
        ticket = self.get_active_ticket()
        suffix = ""
        if ticket is not None:
            suffix = f"\nCurrent status: {self._enum_text(ticket.status)}  |  Aggregate version: {ticket.version}"
        note_line = f"\n{extra_note}" if extra_note else ""
        self.feedback_frame.configure(bg=self.COLORS["error_bg"])
        self.feedback_label.configure(
            text=f"REJECTED: {message}{note_line}{suffix}",
            bg=self.COLORS["error_bg"],
            fg=self.COLORS["error"],
        )

    def set_controls_state(self):
        has_ticket = self.active_ticket_id is not None
        op_state = "normal" if (has_ticket and not self.is_demo_running) else "disabled"
        for btn in self.operation_buttons:
            btn.configure(state=op_state)

        self.create_btn.configure(state="disabled" if (has_ticket or self.is_demo_running) else "normal")
        self.btn_valid_demo.configure(state="disabled" if self.is_demo_running else "normal")
        self.btn_invalid_demo.configure(state="disabled" if self.is_demo_running else "normal")
        self.btn_reset.configure(state="disabled" if self.is_demo_running else "normal")

    def refresh_ticket_details(self):
        ticket = self.get_active_ticket()
        if ticket is None:
            self.status_label.configure(text="NO ACTIVE TICKET", fg=self.COLORS["muted"])
            for key, var in self.detail_vars.items():
                var.set("Not assigned" if key in ("assignee", "priority") else "—")
            return

        status_name = self._enum_text(ticket.status)
        self.status_label.configure(
            text=status_name,
            fg=self.STATUS_COLORS.get(status_name, self.COLORS["navy"]),
        )
        meta = self.ticket_metadata.get(ticket.id.value, {})
        self.detail_vars["id"].set(str(ticket.id.value))
        self.detail_vars["title"].set(meta.get("title", "—"))
        self.detail_vars["category"].set(meta.get("category", "—"))
        self.detail_vars["description"].set(meta.get("description", "—"))
        self.detail_vars["reporter"].set(str(ticket.reporter_id))
        self.detail_vars["assignee"].set(str(ticket.assignee_id) if ticket.assignee_id else "Not assigned")
        self.detail_vars["urgency"].set(self._enum_text(ticket.urgency))
        self.detail_vars["priority"].set(self._enum_text(ticket.priority, default="Not assigned"))
        self.detail_vars["version"].set(str(ticket.version))

        can_write = ConversationPolicy.can_write(ticket, self.get_selected_actor())
        self.detail_vars["chat_access"].set("Allowed" if can_write else "Denied")

    def refresh_event_history(self):
        for item in self.event_tree.get_children():
            self.event_tree.delete(item)

        ticket = self.get_active_ticket()
        if ticket is None:
            return

        for ev in ticket.events:
            self.event_tree.insert(
                "",
                "end",
                values=(
                    ev.version,
                    ev.kind,
                    ev.actor_id,
                    self._enum_text(ev.before, default="—"),
                    self._enum_text(ev.after, default="—"),
                    ev.reason or "—",
                    str(ev.at),
                ),
            )

    def refresh_all(self):
        self.refresh_ticket_details()
        self.refresh_event_history()
        self.set_controls_state()

    def execute_domain_operation(self, operation_fn, success_message: str):
        if self.active_ticket_id is None:
            self.show_error("No active ticket. Create a ticket first.")
            return False
        try:
            ticket = self.repository.get(self.active_ticket_id)
            expected_version = ticket.version
            operation_fn(ticket)
            self.repository.save(ticket, expected_version)
            self.refresh_all()
            self.show_success(success_message)
            return True
        except RuleViolation as exc:
            self.refresh_all()
            self.show_error(str(exc))
            return False
        except Exception as exc:
            self.refresh_all()
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred:\n{exc}")
            return False

    # ------------------------------------------------------------------
    # Manual Operations
    # ------------------------------------------------------------------
    def create_ticket(self):
        if self.active_ticket_id is not None:
            messagebox.showinfo("Active Ticket Exists", "Please click 'Reset Demo' before creating a new ticket.")
            return

        title = self.title_var.get().strip()
        description = self.desc_text.get("1.0", "end").strip()
        category = self.category_var.get().strip()
        urgency = Urgency[self.urgency_var.get()]

        try:
            ticket = SupportTicket(
                self.actors["Reporter"],
                title,
                description,
                category,
                urgency,
            )
            self.repository.add(ticket)
            self.active_ticket_id = ticket.id
            self.ticket_metadata[ticket.id.value] = {
                "title": title,
                "description": description,
                "category": category,
            }
            self.refresh_all()
            self.show_success("Reporter created a new support ticket.")
        except RuleViolation as exc:
            self.show_error(str(exc))
        except Exception as exc:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred:\n{exc}")

    def claim_ticket(self):
        if self.active_ticket_id is None:
            return
        actor_name = self.actor_var.get()
        actor = self.get_selected_actor()
        try:
            ClaimTicket(self.repository).execute(self.active_ticket_id, actor)
            self.refresh_all()
            self.show_success(f"{actor_name} claimed the ticket.")
        except RuleViolation as exc:
            self.refresh_all()
            self.show_error(str(exc))
        except Exception as exc:
            self.refresh_all()
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred:\n{exc}")

    def set_priority(self):
        actor_name = self.actor_var.get()
        actor = self.get_selected_actor()
        priority = Priority[self.priority_var.get()]
        reason = self.reason_var.get().strip()
        if reason == "Optional reason...":
            reason = ""
        self.execute_domain_operation(
            lambda t: t.set_priority(actor, priority, reason),
            f"{actor_name} set official priority to {priority.name}.",
        )

    def start_work(self):
        actor_name = self.actor_var.get()
        actor = self.get_selected_actor()
        self.execute_domain_operation(
            lambda t: t.advance(actor, Status.IN_PROGRESS),
            f"{actor_name} started work on the ticket.",
        )

    def resolve_ticket(self):
        actor_name = self.actor_var.get()
        actor = self.get_selected_actor()
        self.execute_domain_operation(
            lambda t: t.advance(actor, Status.RESOLVED),
            f"{actor_name} resolved the ticket.",
        )

    def close_ticket(self):
        actor_name = self.actor_var.get()
        actor = self.get_selected_actor()
        self.execute_domain_operation(
            lambda t: t.advance(actor, Status.CLOSED),
            f"{actor_name} closed the ticket.",
        )

    def cancel_ticket(self):
        actor_name = self.actor_var.get()
        actor = self.get_selected_actor()
        self.execute_domain_operation(
            lambda t: t.advance(actor, Status.CANCELLED),
            f"{actor_name} cancelled the ticket.",
        )

    def reassign_agent(self):
        actor_name = self.actor_var.get()
        actor = self.get_selected_actor()
        dest_label = self.reassign_var.get()
        dest_agent = self.agent_actors[dest_label]
        self.execute_domain_operation(
            lambda t: t.reassign(actor, dest_agent),
            f"{actor_name} reassigned the ticket to {dest_label}.",
        )

    def check_chat_access(self):
        ticket = self.get_active_ticket()
        if ticket is None:
            return
        actor_name = self.actor_var.get()
        actor = self.get_selected_actor()
        allowed = ConversationPolicy.can_write(ticket, actor)
        self.refresh_ticket_details()
        if allowed:
            self.show_success(f"ConversationPolicy: {actor_name} IS allowed to write in the ticket conversation.")
        else:
            self.show_error(f"ConversationPolicy: {actor_name} is NOT allowed to write in the ticket conversation.")

    def _reset_state(self):
        self.repository = MemoryTicketRepository()
        self.active_ticket_id = None
        self.ticket_metadata.clear()
        self.title_var.set("Wi-Fi connection problem")
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", "Cannot connect to the university network.")
        self.category_var.set("Network")
        self.urgency_var.set(Urgency.HIGH.name)
        self.reason_var.set("Optional reason...")
        self.refresh_all()

    def reset_demo(self):
        if self.active_ticket_id is not None:
            confirm = messagebox.askyesno(
                "Reset Demo",
                "This will clear the current in-memory demonstration and start fresh. Continue?",
            )
            if not confirm:
                return
        self._reset_state()
        self.feedback_frame.configure(bg=self.COLORS["bg"])
        self.feedback_label.configure(
            text="Demo reset. Ready to create a new ticket or run a scenario.",
            bg=self.COLORS["bg"],
            fg=self.COLORS["text"],
        )

    # ------------------------------------------------------------------
    # Automated Demonstration Scenarios
    # ------------------------------------------------------------------
    def _confirm_demo_reset(self) -> bool:
        if self.active_ticket_id is not None:
            return messagebox.askyesno(
                "Start Automated Scenario",
                "Starting an automated scenario will reset the current demonstration. Continue?",
            )
        return True

    def _run_steps(self, steps, index=0):
        if index >= len(steps):
            self.is_demo_running = False
            self.set_controls_state()
            return
        steps[index]()
        self.root.after(650, lambda: self._run_steps(steps, index + 1))

    def run_valid_demo(self):
        if not self._confirm_demo_reset():
            return
        self._reset_state()
        self.is_demo_running = True
        self.set_controls_state()

        agent_a = self.actors["Support Agent A"]
        reporter = self.actors["Reporter"]

        def step_create():
            self.actor_var.set("Reporter")
            self.create_ticket()

        def step_claim():
            self.actor_var.set("Support Agent A")
            ClaimTicket(self.repository).execute(self.active_ticket_id, agent_a)
            self.refresh_all()
            self.show_success("Step 2/6: Support Agent A claimed the ticket.")

        def step_priority():
            self.execute_domain_operation(
                lambda t: t.set_priority(agent_a, Priority.P2_HIGH, ""),
                "Step 3/6: Support Agent A assigned P2_HIGH official priority.",
            )

        def step_start():
            self.execute_domain_operation(
                lambda t: t.advance(agent_a, Status.IN_PROGRESS),
                "Step 4/6: Support Agent A started work (IN_PROGRESS).",
            )

        def step_resolve():
            self.execute_domain_operation(
                lambda t: t.advance(agent_a, Status.RESOLVED),
                "Step 5/6: Support Agent A resolved the ticket (RESOLVED).",
            )

        def step_close():
            self.actor_var.set("Reporter")
            self.execute_domain_operation(
                lambda t: t.advance(reporter, Status.CLOSED),
                "Step 6/6: Reporter closed the ticket. Valid lifecycle completed!",
            )

        self._run_steps([step_create, step_claim, step_priority, step_start, step_resolve, step_close])

    def run_invalid_demo(self):
        if not self._confirm_demo_reset():
            return
        self._reset_state()
        self.is_demo_running = True
        self.set_controls_state()

        agent_a = self.actors["Support Agent A"]

        def step_create():
            self.actor_var.set("Reporter")
            self.create_ticket()

        def step_claim():
            self.actor_var.set("Support Agent A")
            ClaimTicket(self.repository).execute(self.active_ticket_id, agent_a)
            self.refresh_all()
            self.show_success("Step 2/3: Support Agent A claimed the ticket (no priority assigned).")

        def step_invalid_start():
            try:
                ticket = self.repository.get(self.active_ticket_id)
                expected_version = ticket.version
                ticket.advance(agent_a, Status.IN_PROGRESS)
                self.repository.save(ticket, expected_version)
                self.refresh_all()
            except RuleViolation as exc:
                self.refresh_all()
                self.show_error(
                    str(exc),
                    extra_note="The domain model rejected the operation because an official priority must be assigned before work can begin.",
                )

        self._run_steps([step_create, step_claim, step_invalid_start])


if __name__ == "__main__":
    root = tk.Tk()
    app = FixItGUI(root)
    root.mainloop()
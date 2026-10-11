"""Tkinter frontend for the bank app.

Run with:  python3 bank_app.py

The UI talks only to a `bank` object (currently MockBank). When the C++
backend is ready, pass that in instead - see mock_bank.py for the contract.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from mock_bank import MockBank


def fmt_money(amount: float) -> str:
    return f"${amount:,.2f}"


class BankApp(tk.Tk):
    def __init__(self, bank) -> None:
        super().__init__()
        self.bank = bank
        self.selected_id: Optional[str] = None

        self.title("Bank App (MVP - mock data)")
        self.geometry("980x560")
        self.minsize(820, 460)

        self._build_layout()
        self.refresh_accounts()

    # --- Layout ----------------------------------------------------------

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        self._build_accounts_pane()
        self._build_details_pane()
        self._build_status_bar()

    def _build_accounts_pane(self) -> None:
        pane = ttk.LabelFrame(self, text="Accounts", padding=8)
        pane.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        pane.rowconfigure(0, weight=1)
        pane.columnconfigure(0, weight=1)

        cols = ("id", "owner", "type", "balance")
        self.accounts_tree = ttk.Treeview(pane, columns=cols, show="headings", selectmode="browse")
        for col, heading, width, anchor in [
            ("id", "ID", 90, "w"),
            ("owner", "Owner", 130, "w"),
            ("type", "Type", 80, "w"),
            ("balance", "Balance", 100, "e"),
        ]:
            self.accounts_tree.heading(col, text=heading, anchor=anchor)
            self.accounts_tree.column(col, width=width, anchor=anchor)
        self.accounts_tree.grid(row=0, column=0, sticky="nsew")
        self.accounts_tree.bind("<<TreeviewSelect>>", self._on_account_selected)

    def _build_details_pane(self) -> None:
        pane = ttk.LabelFrame(self, text="Account details", padding=8)
        pane.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        pane.columnconfigure(0, weight=1)
        pane.rowconfigure(3, weight=1)

        self.owner_var = tk.StringVar(value="Select an account")
        self.type_var = tk.StringVar(value="")
        self.balance_var = tk.StringVar(value="")

        header = ttk.Frame(pane)
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, textvariable=self.owner_var, font=("TkDefaultFont", 14, "bold")).pack(anchor="w")
        ttk.Label(header, textvariable=self.type_var).pack(anchor="w")
        ttk.Label(header, textvariable=self.balance_var, font=("TkDefaultFont", 24, "bold")).pack(
            anchor="w", pady=(4, 8)
        )

        actions = ttk.Frame(pane)
        actions.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(actions, text="Amount $").pack(side="left")
        self.amount_var = tk.StringVar()
        ttk.Entry(actions, textvariable=self.amount_var, width=12).pack(side="left", padx=(2, 8))
        ttk.Button(actions, text="Deposit", command=self._on_deposit).pack(side="left")
        ttk.Button(actions, text="Withdraw", command=self._on_withdraw).pack(side="left", padx=4)
        ttk.Button(actions, text="Transfer…", command=self._on_transfer).pack(side="left")

        ttk.Label(pane, text="Transaction history").grid(row=2, column=0, sticky="w")

        cols = ("date", "kind", "amount", "note")
        self.history_tree = ttk.Treeview(pane, columns=cols, show="headings", selectmode="none")
        for col, heading, width, anchor in [
            ("date", "Date", 130, "w"),
            ("kind", "Type", 100, "w"),
            ("amount", "Amount", 90, "e"),
            ("note", "Note", 160, "w"),
        ]:
            self.history_tree.heading(col, text=heading, anchor=anchor)
            self.history_tree.column(col, width=width, anchor=anchor)
        self.history_tree.grid(row=3, column=0, sticky="nsew")

    def _build_status_bar(self) -> None:
        self.status_var = tk.StringVar(value="Ready - using mock data")
        ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w", padding=(6, 2)).grid(
            row=1, column=0, columnspan=2, sticky="ew"
        )

    # --- Refresh ---------------------------------------------------------

    def refresh_accounts(self) -> None:
        self.accounts_tree.delete(*self.accounts_tree.get_children())
        for acc in self.bank.list_accounts():
            self.accounts_tree.insert(
                "",
                "end",
                iid=acc.account_id,
                values=(acc.account_id, acc.owner, acc.account_type, fmt_money(acc.balance)),
            )
        if self.selected_id is None:
            children = self.accounts_tree.get_children()
            if children:
                self.selected_id = children[0]
        if self.selected_id is not None:
            self.accounts_tree.selection_set(self.selected_id)
        self.refresh_details()

    def refresh_details(self) -> None:
        self.history_tree.delete(*self.history_tree.get_children())
        if self.selected_id is None:
            return
        acc = self.bank.get_account(self.selected_id)
        self.owner_var.set(acc.owner)
        self.type_var.set(f"{acc.account_type} · {acc.account_id}")
        self.balance_var.set(fmt_money(acc.balance))
        for txn in self.bank.get_transactions(acc.account_id):
            sign = "+" if txn.kind in ("Deposit", "Transfer In") else "-"
            self.history_tree.insert(
                "",
                "end",
                values=(
                    txn.timestamp.strftime("%Y-%m-%d %H:%M"),
                    txn.kind,
                    f"{sign}{fmt_money(txn.amount)}",
                    txn.note,
                ),
            )

    def _on_account_selected(self, _event=None) -> None:
        selection = self.accounts_tree.selection()
        if selection and selection[0] != self.selected_id:
            self.selected_id = selection[0]
            self.refresh_details()

    # --- Actions ---------------------------------------------------------

    def _parse_amount(self, raw: str) -> Optional[float]:
        try:
            return float(raw.strip().replace(",", "").lstrip("$"))
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter a valid amount.", parent=self)
            return None

    def _run_action(self, title: str, action, success_msg: str) -> bool:
        """Call a bank operation, showing its ValueError to the user on failure."""
        try:
            action()
        except ValueError as err:
            messagebox.showerror(title, str(err), parent=self)
            return False
        self.amount_var.set("")
        self.status_var.set(success_msg)
        self.refresh_accounts()
        return True

    def _on_deposit(self) -> None:
        amount = self._parse_amount(self.amount_var.get())
        if amount is None or self.selected_id is None:
            return
        acc_id = self.selected_id
        self._run_action(
            "Deposit failed",
            lambda: self.bank.deposit(acc_id, amount),
            f"Deposited {fmt_money(amount)} to {acc_id}",
        )

    def _on_withdraw(self) -> None:
        amount = self._parse_amount(self.amount_var.get())
        if amount is None or self.selected_id is None:
            return
        acc_id = self.selected_id
        self._run_action(
            "Withdrawal failed",
            lambda: self.bank.withdraw(acc_id, amount),
            f"Withdrew {fmt_money(amount)} from {acc_id}",
        )

    def _on_transfer(self) -> None:
        if self.selected_id is not None:
            TransferDialog(self, self.selected_id)


class TransferDialog(tk.Toplevel):
    def __init__(self, app: BankApp, from_id: str) -> None:
        super().__init__(app)
        self.app = app
        self.from_id = from_id

        self.title("Transfer")
        self.resizable(False, False)
        self.transient(app)

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text=f"From: {from_id}").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        ttk.Label(body, text="To:").grid(row=1, column=0, sticky="w")
        destinations = [
            f"{acc.account_id} - {acc.owner} ({acc.account_type})"
            for acc in app.bank.list_accounts()
            if acc.account_id != from_id
        ]
        self.dest_var = tk.StringVar(value=destinations[0] if destinations else "")
        ttk.Combobox(body, textvariable=self.dest_var, values=destinations, state="readonly", width=34).grid(
            row=1, column=1, sticky="ew", pady=2
        )

        ttk.Label(body, text="Amount $").grid(row=2, column=0, sticky="w")
        self.amount_var = tk.StringVar(value=app.amount_var.get())
        entry = ttk.Entry(body, textvariable=self.amount_var, width=12)
        entry.grid(row=2, column=1, sticky="w", pady=2)

        buttons = ttk.Frame(body)
        buttons.grid(row=3, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Transfer", command=self._submit).pack(side="right", padx=(0, 6))

        self.bind("<Return>", lambda _e: self._submit())
        self.bind("<Escape>", lambda _e: self.destroy())
        entry.focus_set()
        self.grab_set()

    def _submit(self) -> None:
        amount = self.app._parse_amount(self.amount_var.get())
        if amount is None or not self.dest_var.get():
            return
        to_id = self.dest_var.get().split(" - ", 1)[0]
        if self.app._run_action(
            "Transfer failed",
            lambda: self.app.bank.transfer(self.from_id, to_id, amount),
            f"Transferred {fmt_money(amount)} from {self.from_id} to {to_id}",
        ):
            self.destroy()


def main() -> None:
    app = BankApp(MockBank())
    app.mainloop()


if __name__ == "__main__":
    main()

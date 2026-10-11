"""Tkinter frontend for the bank app.

Run with:  python3 bank_app.py

The UI talks only to a `bank` object (currently MockBank). When the C++
backend is ready, pass that in instead - see mock_bank.py for the contract.
"""

import tkinter as tk
from tkinter import ttk
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
        pane.rowconfigure(2, weight=1)

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

        ttk.Label(pane, text="Transaction history").grid(row=1, column=0, sticky="w")

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
        self.history_tree.grid(row=2, column=0, sticky="nsew")

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


def main() -> None:
    app = BankApp(MockBank())
    app.mainloop()


if __name__ == "__main__":
    main()

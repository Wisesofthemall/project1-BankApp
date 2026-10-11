"""In-memory stand-in for the C++ backend.

The public methods of MockBank are the contract the real backend
(exposed to Python through bank_wrapper.cpp) must satisfy. The UI only
calls these methods, so swapping MockBank for the real thing should not
require UI changes.

Errors are raised as ValueError with a message meant to be shown to the
user as-is.
"""

import copy
from datetime import datetime
from typing import Dict, List

from mock_data import SEED_ACCOUNTS, SEED_TRANSACTIONS, Account, Transaction


class MockBank:
    def __init__(self) -> None:
        self._accounts: Dict[str, Account] = {
            acc.account_id: acc for acc in copy.deepcopy(SEED_ACCOUNTS)
        }
        self._transactions: List[Transaction] = copy.deepcopy(SEED_TRANSACTIONS)
        self._next_txn_id = max((t.txn_id for t in self._transactions), default=0) + 1

    # --- Queries ---------------------------------------------------------

    def list_accounts(self) -> List[Account]:
        return [copy.copy(acc) for acc in self._accounts.values()]

    def get_account(self, account_id: str) -> Account:
        return copy.copy(self._require_account(account_id))

    def get_transactions(self, account_id: str) -> List[Transaction]:
        self._require_account(account_id)
        txns = [copy.copy(t) for t in self._transactions if t.account_id == account_id]
        txns.sort(key=lambda t: (t.timestamp, t.txn_id), reverse=True)
        return txns

    # --- Commands --------------------------------------------------------

    def deposit(self, account_id: str, amount: float) -> None:
        acc = self._require_account(account_id)
        amount = self._validate_amount(amount)
        acc.balance = round(acc.balance + amount, 2)
        self._record(account_id, "Deposit", amount)

    def withdraw(self, account_id: str, amount: float) -> None:
        acc = self._require_account(account_id)
        amount = self._validate_amount(amount)
        self._require_funds(acc, amount)
        acc.balance = round(acc.balance - amount, 2)
        self._record(account_id, "Withdrawal", amount)

    def transfer(self, from_id: str, to_id: str, amount: float) -> None:
        if from_id == to_id:
            raise ValueError("Cannot transfer to the same account.")
        src = self._require_account(from_id)
        dst = self._require_account(to_id)
        amount = self._validate_amount(amount)
        self._require_funds(src, amount)
        src.balance = round(src.balance - amount, 2)
        dst.balance = round(dst.balance + amount, 2)
        now = datetime.now()
        self._record(from_id, "Transfer Out", amount, f"To {to_id}", now)
        self._record(to_id, "Transfer In", amount, f"From {from_id}", now)

    # --- Helpers ---------------------------------------------------------

    def _require_account(self, account_id: str) -> Account:
        acc = self._accounts.get(account_id)
        if acc is None:
            raise ValueError(f"Account {account_id} does not exist.")
        return acc

    @staticmethod
    def _validate_amount(amount: float) -> float:
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(float(amount), 2)

    @staticmethod
    def _require_funds(acc: Account, amount: float) -> None:
        if amount > acc.balance:
            raise ValueError(
                f"Insufficient funds in {acc.account_id} (balance ${acc.balance:,.2f})."
            )

    def _record(self, account_id, kind, amount, note="", timestamp=None) -> None:
        self._transactions.append(
            Transaction(
                self._next_txn_id,
                account_id,
                kind,
                amount,
                timestamp or datetime.now(),
                note,
            )
        )
        self._next_txn_id += 1

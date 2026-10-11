"""Seed data for the MVP frontend.

Plain data only - no behavior. MockBank copies this on startup, so every
run of the app begins from the same state.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Account:
    account_id: str
    owner: str
    account_type: str  # "Checking" or "Savings"
    balance: float


@dataclass
class Transaction:
    txn_id: int
    account_id: str
    kind: str  # "Deposit", "Withdrawal", "Transfer In", "Transfer Out"
    amount: float
    timestamp: datetime
    note: str = ""


SEED_ACCOUNTS = [
    Account("ACC-1001", "Alice Johnson", "Checking", 2450.75),
    Account("ACC-1002", "Alice Johnson", "Savings", 10200.00),
    Account("ACC-2001", "Marcus Lee", "Checking", 318.40),
    Account("ACC-3001", "Priya Patel", "Savings", 5875.10),
]

SEED_TRANSACTIONS = [
    Transaction(1, "ACC-1001", "Deposit", 1500.00, datetime(2026, 9, 1, 9, 15), "Paycheck"),
    Transaction(2, "ACC-1001", "Withdrawal", 120.25, datetime(2026, 9, 3, 18, 40), "Groceries"),
    Transaction(3, "ACC-1001", "Transfer Out", 500.00, datetime(2026, 9, 5, 12, 0), "To ACC-1002"),
    Transaction(4, "ACC-1002", "Transfer In", 500.00, datetime(2026, 9, 5, 12, 0), "From ACC-1001"),
    Transaction(5, "ACC-2001", "Deposit", 400.00, datetime(2026, 9, 7, 10, 30), "Cash deposit"),
    Transaction(6, "ACC-2001", "Withdrawal", 81.60, datetime(2026, 9, 9, 20, 5), "Utilities"),
    Transaction(7, "ACC-3001", "Deposit", 2000.00, datetime(2026, 9, 12, 8, 45), "Bonus"),
    Transaction(8, "ACC-1002", "Deposit", 200.00, datetime(2026, 9, 20, 14, 10), "Interest"),
    Transaction(9, "ACC-3001", "Withdrawal", 124.90, datetime(2026, 9, 25, 16, 20), "Phone bill"),
    Transaction(10, "ACC-1001", "Withdrawal", 64.00, datetime(2026, 10, 2, 11, 55), "Gas"),
]

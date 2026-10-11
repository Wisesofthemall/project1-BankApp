# project1-BankApp
Build a banking application with a C++ backend and Python/Tkinter frontend, applying OOP, file handling, memory management, input validation, and cross-language integration.

## Running the frontend

```bash
python3 bank_app.py
```

Only the Python standard library is needed. You need a Python build with a working Tk 8.6. On macOS, Apple's bundled `/usr/bin/python3` ships the deprecated Tk 8.5, which can hang on startup. Use Homebrew instead (`brew install python-tk`, then run with `/opt/homebrew/bin/python3`) or the python.org installer.

The current version is an MVP that runs on **mock data**. You can browse accounts, view transaction history, and deposit, withdraw and transfer money. Nothing is saved, and every run starts from the same seed data.

## Project layout

| File | Purpose |
| --- | --- |
| `bank_app.py` | Tkinter UI and entry point |
| `mock_bank.py` | `MockBank`, an in-memory stand-in for the C++ backend |
| `mock_data.py` | `Account`/`Transaction` models and seed data |
| `bank.h`, `bank.cpp`, `main.cpp` | C++ backend (not started yet) |
| `bank_wrapper.cpp` | Python bindings for the C++ backend (not started yet) |

## Path to the real backend

The UI only talks to the object passed into `BankApp(...)`. `MockBank`'s public methods (`list_accounts`, `get_account`, `get_transactions`, `deposit`, `withdraw`, `transfer`) are the contract the C++ backend must implement and expose through `bank_wrapper.cpp`. When that backend exists, `main()` in `bank_app.py` passes it in place of `MockBank()`.

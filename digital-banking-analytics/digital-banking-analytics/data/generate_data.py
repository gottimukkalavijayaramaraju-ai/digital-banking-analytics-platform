"""
generate_data.py
Generates a realistic sample dataset for the Digital Banking Analytics Platform
and stores it in a local SQLite database (data/banking.db).

Run:
    python data/generate_data.py
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

DB_PATH = Path(__file__).parent / "banking.db"

FIRST_NAMES = ["Aditi", "Rahul", "Priya", "Vikram", "Sneha", "Arjun", "Kavya",
               "Rohan", "Meera", "Karan", "Anjali", "Sanjay", "Divya", "Amit",
               "Neha", "Suresh", "Pooja", "Manoj", "Isha", "Ravi"]
LAST_NAMES = ["Sharma", "Verma", "Iyer", "Reddy", "Gupta", "Nair", "Patel",
              "Singh", "Das", "Menon", "Rao", "Kapoor", "Chatterjee", "Joshi"]

ACCOUNT_TYPES = ["SAVINGS", "CURRENT", "SALARY", "FIXED_DEPOSIT"]
CITIES = ["Hyderabad", "Mumbai", "Bengaluru", "Delhi", "Chennai", "Pune", "Kolkata"]

CATEGORIES = ["Groceries", "Utilities", "Dining", "Shopping", "Travel",
              "Healthcare", "Entertainment", "Rent", "Salary Credit",
              "Investment", "ATM Withdrawal", "Fuel", "Insurance", "Education"]

TXN_TYPES = ["DEBIT", "CREDIT"]

NUM_CUSTOMERS = 150
NUM_ACCOUNTS_PER_CUSTOMER = (1, 2)
NUM_DAYS_OF_HISTORY = 180
AVG_TXNS_PER_ACCOUNT_PER_DAY = 0.6


def create_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS transactions;
        DROP TABLE IF EXISTS accounts;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            customer_id     INTEGER PRIMARY KEY,
            first_name      TEXT NOT NULL,
            last_name       TEXT NOT NULL,
            email           TEXT NOT NULL,
            city            TEXT NOT NULL,
            signup_date     TEXT NOT NULL,
            age             INTEGER NOT NULL,
            risk_segment    TEXT NOT NULL
        );

        CREATE TABLE accounts (
            account_id      INTEGER PRIMARY KEY,
            customer_id     INTEGER NOT NULL,
            account_type    TEXT NOT NULL,
            opened_date     TEXT NOT NULL,
            balance         REAL NOT NULL,
            status          TEXT NOT NULL DEFAULT 'ACTIVE',
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE transactions (
            transaction_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id      INTEGER NOT NULL,
            txn_date        TEXT NOT NULL,
            txn_type        TEXT NOT NULL,
            category        TEXT NOT NULL,
            amount          REAL NOT NULL,
            merchant        TEXT,
            is_flagged      INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        );

        CREATE INDEX idx_txn_account ON transactions(account_id);
        CREATE INDEX idx_txn_date ON transactions(txn_date);
        CREATE INDEX idx_account_customer ON accounts(customer_id);
        """
    )
    conn.commit()


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_customers(conn: sqlite3.Connection):
    cur = conn.cursor()
    today = datetime.now()
    rows = []
    for cid in range(1, NUM_CUSTOMERS + 1):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        email = f"{fn.lower()}.{ln.lower()}{cid}@example.com"
        city = random.choice(CITIES)
        signup = random_date(today - timedelta(days=900), today - timedelta(days=30))
        age = random.randint(19, 70)
        risk_segment = random.choices(
            ["LOW", "MEDIUM", "HIGH"], weights=[0.65, 0.28, 0.07]
        )[0]
        rows.append((cid, fn, ln, email, city, signup.strftime("%Y-%m-%d"), age, risk_segment))

    cur.executemany(
        """INSERT INTO customers
           (customer_id, first_name, last_name, email, city, signup_date, age, risk_segment)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()


def generate_accounts(conn: sqlite3.Connection):
    cur = conn.cursor()
    today = datetime.now()
    account_id = 1
    rows = []
    account_map = {}  # customer_id -> [account_ids]

    for cid in range(1, NUM_CUSTOMERS + 1):
        n_accounts = random.randint(*NUM_ACCOUNTS_PER_CUSTOMER)
        account_map[cid] = []
        for _ in range(n_accounts):
            acc_type = random.choice(ACCOUNT_TYPES)
            opened = random_date(today - timedelta(days=800), today - timedelta(days=10))
            balance = round(random.uniform(500, 500000), 2)
            status = random.choices(["ACTIVE", "DORMANT", "CLOSED"], weights=[0.88, 0.08, 0.04])[0]
            rows.append((account_id, cid, acc_type, opened.strftime("%Y-%m-%d"), balance, status))
            account_map[cid].append(account_id)
            account_id += 1

    cur.executemany(
        """INSERT INTO accounts
           (account_id, customer_id, account_type, opened_date, balance, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()
    return account_map


def generate_transactions(conn: sqlite3.Connection, account_map: dict):
    cur = conn.cursor()
    today = datetime.now()
    start_date = today - timedelta(days=NUM_DAYS_OF_HISTORY)

    all_account_ids = [aid for accs in account_map.values() for aid in accs]
    rows = []

    for account_id in all_account_ids:
        expected_txns = int(NUM_DAYS_OF_HISTORY * AVG_TXNS_PER_ACCOUNT_PER_DAY)
        num_txns = max(1, int(random.gauss(expected_txns, expected_txns * 0.3)))

        for _ in range(num_txns):
            txn_date = random_date(start_date, today)
            category = random.choice(CATEGORIES)
            txn_type = "CREDIT" if category in ("Salary Credit", "Investment") else random.choices(
                TXN_TYPES, weights=[0.82, 0.18]
            )[0]

            if category == "Salary Credit":
                amount = round(random.uniform(25000, 150000), 2)
            elif category == "Rent":
                amount = round(random.uniform(8000, 45000), 2)
            elif category == "ATM Withdrawal":
                amount = round(random.choice([1000, 2000, 5000, 10000]), 2)
            else:
                amount = round(random.uniform(50, 15000), 2)

            # occasionally simulate a large / odd-hour transaction to flag as suspicious
            is_flagged = 0
            if txn_type == "DEBIT" and amount > 40000 and random.random() < 0.5:
                is_flagged = 1
            elif random.random() < 0.01:
                amount = round(amount * random.uniform(3, 8), 2)
                is_flagged = 1

            merchant = f"{category} Merchant {random.randint(1, 40)}"
            rows.append((
                account_id,
                txn_date.strftime("%Y-%m-%d %H:%M:%S"),
                txn_type,
                category,
                amount,
                merchant,
                is_flagged,
            ))

    cur.executemany(
        """INSERT INTO transactions
           (account_id, txn_date, txn_type, category, amount, merchant, is_flagged)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()
    print(f"Inserted {len(rows)} transactions.")


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)
    generate_customers(conn)
    account_map = generate_accounts(conn)
    generate_transactions(conn, account_map)
    conn.close()

    print(f"Database created at: {DB_PATH}")
    print(f"Customers: {NUM_CUSTOMERS}")
    print(f"Accounts: {sum(len(v) for v in account_map.values())}")


if __name__ == "__main__":
    main()

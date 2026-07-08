"""
analytics.py
All analytics/query logic lives here, decoupled from the API layer,
so it can be reused by both FastAPI endpoints and the Streamlit dashboard.
"""

from app.database import get_connection, rows_to_dicts
import pandas as pd


def get_summary_kpis() -> dict:
    conn = get_connection()
    total_customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    total_accounts = conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    active_accounts = conn.execute(
        "SELECT COUNT(*) FROM accounts WHERE status='ACTIVE'"
    ).fetchone()[0]
    total_balance = conn.execute("SELECT SUM(balance) FROM accounts").fetchone()[0] or 0
    total_txns = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    flagged_txns = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE is_flagged=1"
    ).fetchone()[0]
    total_debit = conn.execute(
        "SELECT SUM(amount) FROM transactions WHERE txn_type='DEBIT'"
    ).fetchone()[0] or 0
    total_credit = conn.execute(
        "SELECT SUM(amount) FROM transactions WHERE txn_type='CREDIT'"
    ).fetchone()[0] or 0
    conn.close()

    return {
        "total_customers": total_customers,
        "total_accounts": total_accounts,
        "active_accounts": active_accounts,
        "total_balance": round(total_balance, 2),
        "total_transactions": total_txns,
        "flagged_transactions": flagged_txns,
        "total_debit_volume": round(total_debit, 2),
        "total_credit_volume": round(total_credit, 2),
    }


def get_daily_transaction_trend(days: int = 90) -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT DATE(txn_date) AS day,
               txn_type,
               SUM(amount) AS total_amount,
               COUNT(*) AS txn_count
        FROM transactions
        WHERE DATE(txn_date) >= DATE('now', ?)
        GROUP BY day, txn_type
        ORDER BY day
    """
    df = pd.read_sql_query(query, conn, params=(f"-{days} days",))
    conn.close()
    return df


def get_spending_by_category() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT category, SUM(amount) AS total_amount, COUNT(*) AS txn_count
        FROM transactions
        WHERE txn_type = 'DEBIT'
        GROUP BY category
        ORDER BY total_amount DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_account_type_distribution() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT account_type, COUNT(*) AS num_accounts, SUM(balance) AS total_balance
        FROM accounts
        GROUP BY account_type
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_customer_city_distribution() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT city, COUNT(*) AS num_customers
        FROM customers
        GROUP BY city
        ORDER BY num_customers DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_top_customers_by_balance(limit: int = 10) -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT c.customer_id, c.first_name || ' ' || c.last_name AS customer_name,
               c.city, SUM(a.balance) AS total_balance, COUNT(a.account_id) AS num_accounts
        FROM customers c
        JOIN accounts a ON a.customer_id = c.customer_id
        GROUP BY c.customer_id
        ORDER BY total_balance DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df


def get_flagged_transactions(limit: int = 50) -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT t.transaction_id, t.txn_date, t.account_id, a.customer_id,
               c.first_name || ' ' || c.last_name AS customer_name,
               t.txn_type, t.category, t.amount, t.merchant
        FROM transactions t
        JOIN accounts a ON a.account_id = t.account_id
        JOIN customers c ON c.customer_id = a.customer_id
        WHERE t.is_flagged = 1
        ORDER BY t.txn_date DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df


def get_monthly_active_accounts() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT strftime('%Y-%m', txn_date) AS month,
               COUNT(DISTINCT account_id) AS active_accounts
        FROM transactions
        GROUP BY month
        ORDER BY month
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def search_customer(name_query: str) -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT c.customer_id, c.first_name || ' ' || c.last_name AS customer_name,
               c.email, c.city, c.age, c.risk_segment,
               COUNT(a.account_id) AS num_accounts, SUM(a.balance) AS total_balance
        FROM customers c
        LEFT JOIN accounts a ON a.customer_id = c.customer_id
        WHERE LOWER(c.first_name || ' ' || c.last_name) LIKE LOWER(?)
        GROUP BY c.customer_id
    """
    df = pd.read_sql_query(query, conn, params=(f"%{name_query}%",))
    conn.close()
    return df

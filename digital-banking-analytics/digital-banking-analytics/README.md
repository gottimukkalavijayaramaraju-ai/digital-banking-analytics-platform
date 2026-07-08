# Digital Banking Analytics Platform

A simple base project for a digital banking analytics platform. It includes:

- **Synthetic data generator** — creates realistic customers, accounts, and transactions in a local SQLite database.
- **FastAPI backend** — REST API exposing analytics endpoints (KPIs, trends, spending breakdowns, fraud flags, customer search).
- **Streamlit dashboard** — interactive visual analytics UI on top of the same data layer.

## Project Structure

```
digital-banking-analytics/
├── app/
│   ├── __init__.py
│   ├── database.py       # SQLite connection helper
│   ├── analytics.py       # Reusable analytics/query layer
│   └── main.py            # FastAPI app & endpoints
├── dashboard/
│   └── dashboard.py        # Streamlit dashboard
├── data/
│   ├── generate_data.py   # Sample data generator
│   └── banking.db          # Created after running the generator
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate sample data (creates data/banking.db)
python data/generate_data.py
```

## Run the API

```bash
uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000/docs for interactive API documentation.

### Key Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/kpis` | High-level summary metrics |
| `GET /api/transactions/trend?days=90` | Daily transaction volume/count |
| `GET /api/spending/by-category` | Spend breakdown by category |
| `GET /api/accounts/distribution` | Accounts & balances by type |
| `GET /api/customers/by-city` | Customer distribution by city |
| `GET /api/customers/top-balance?limit=10` | Top customers by total balance |
| `GET /api/transactions/flagged?limit=50` | Rule-flagged suspicious transactions |
| `GET /api/accounts/monthly-active` | Monthly active accounts |
| `GET /api/customers/search?name=...` | Search customers by name |

## Run the Dashboard

```bash
streamlit run dashboard/dashboard.py
```

This opens an interactive dashboard with:
- KPI summary cards
- Transaction trend charts
- Spending-by-category breakdown
- Account type distribution
- Customer city distribution & top balances
- Flagged/suspicious transaction review
- Customer search

## Data Model

- **customers**: `customer_id, first_name, last_name, email, city, signup_date, age, risk_segment`
- **accounts**: `account_id, customer_id, account_type, opened_date, balance, status`
- **transactions**: `transaction_id, account_id, txn_date, txn_type, category, amount, merchant, is_flagged`

## Extending This Base Project

- Swap SQLite for PostgreSQL/MySQL by changing `app/database.py`.
- Add authentication (e.g., OAuth2/JWT) to the FastAPI backend.
- Replace the rule-based fraud flags in `data/generate_data.py` / `app/analytics.py` with a trained ML model.
- Add a proper frontend (React/Next.js) that consumes the FastAPI endpoints instead of, or alongside, Streamlit.
- Add scheduled ETL jobs to ingest real transaction feeds instead of synthetic data.

"""
main.py
FastAPI backend for the Digital Banking Analytics Platform.

Run:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app import analytics

app = FastAPI(
    title="Digital Banking Analytics Platform API",
    description="Backend analytics API for accounts, transactions, and customer insights.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "Digital Banking Analytics Platform API"}


@app.get("/api/kpis")
def kpis():
    try:
        return analytics.get_summary_kpis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transactions/trend")
def transaction_trend(days: int = Query(90, ge=1, le=365)):
    df = analytics.get_daily_transaction_trend(days)
    return df.to_dict(orient="records")


@app.get("/api/spending/by-category")
def spending_by_category():
    df = analytics.get_spending_by_category()
    return df.to_dict(orient="records")


@app.get("/api/accounts/distribution")
def account_distribution():
    df = analytics.get_account_type_distribution()
    return df.to_dict(orient="records")


@app.get("/api/customers/by-city")
def customers_by_city():
    df = analytics.get_customer_city_distribution()
    return df.to_dict(orient="records")


@app.get("/api/customers/top-balance")
def top_customers(limit: int = Query(10, ge=1, le=100)):
    df = analytics.get_top_customers_by_balance(limit)
    return df.to_dict(orient="records")


@app.get("/api/transactions/flagged")
def flagged_transactions(limit: int = Query(50, ge=1, le=500)):
    df = analytics.get_flagged_transactions(limit)
    return df.to_dict(orient="records")


@app.get("/api/accounts/monthly-active")
def monthly_active_accounts():
    df = analytics.get_monthly_active_accounts()
    return df.to_dict(orient="records")


@app.get("/api/customers/search")
def search_customer(name: str = Query(..., min_length=1)):
    df = analytics.search_customer(name)
    return df.to_dict(orient="records")

"""
dashboard.py
Streamlit dashboard for the Digital Banking Analytics Platform.

Run:
    streamlit run dashboard/dashboard.py
"""

import sys
from pathlib import Path

# allow importing the `app` package when running via `streamlit run`
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px

from app import analytics

st.set_page_config(
    page_title="Digital Banking Analytics Platform",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 Digital Banking Analytics Platform")
st.caption("Base analytics dashboard — accounts, transactions, customers, and fraud signals.")

# ---------- KPI ROW ----------
try:
    kpis = analytics.get_summary_kpis()
except Exception:
    st.error(
        "No database found. Run `python data/generate_data.py` first to create sample data."
    )
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", f"{kpis['total_customers']:,}")
col2.metric("Accounts", f"{kpis['total_accounts']:,}", f"{kpis['active_accounts']} active")
col3.metric("Total Balance", f"₹{kpis['total_balance']:,.0f}")
col4.metric("Flagged Txns", f"{kpis['flagged_transactions']:,}",
            delta_color="inverse")

col5, col6, col7 = st.columns(3)
col5.metric("Total Transactions", f"{kpis['total_transactions']:,}")
col6.metric("Total Debit Volume", f"₹{kpis['total_debit_volume']:,.0f}")
col7.metric("Total Credit Volume", f"₹{kpis['total_credit_volume']:,.0f}")

st.divider()

# ---------- TABS ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Transaction Trends", "💳 Spending & Accounts", "👥 Customers", "🚨 Fraud Signals", "🔍 Customer Lookup"]
)

with tab1:
    st.subheader("Daily Transaction Volume")
    days = st.slider("Time window (days)", min_value=7, max_value=180, value=90, step=7)
    trend_df = analytics.get_daily_transaction_trend(days)

    if trend_df.empty:
        st.info("No transaction data available for this window.")
    else:
        fig = px.line(
            trend_df, x="day", y="total_amount", color="txn_type",
            markers=True, title="Transaction Amount Over Time",
            labels={"day": "Date", "total_amount": "Amount (₹)", "txn_type": "Type"},
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.bar(
            trend_df, x="day", y="txn_count", color="txn_type",
            title="Transaction Count Over Time",
            labels={"day": "Date", "txn_count": "Count", "txn_type": "Type"},
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Monthly Active Accounts")
    mau_df = analytics.get_monthly_active_accounts()
    if not mau_df.empty:
        fig3 = px.bar(mau_df, x="month", y="active_accounts",
                       title="Accounts with at least 1 transaction per month")
        st.plotly_chart(fig3, use_container_width=True)

with tab2:
    left, right = st.columns(2)

    with left:
        st.subheader("Spending by Category")
        cat_df = analytics.get_spending_by_category()
        fig4 = px.pie(cat_df, names="category", values="total_amount", hole=0.4)
        st.plotly_chart(fig4, use_container_width=True)
        st.dataframe(cat_df, use_container_width=True, hide_index=True)

    with right:
        st.subheader("Account Type Distribution")
        acc_df = analytics.get_account_type_distribution()
        fig5 = px.bar(acc_df, x="account_type", y="num_accounts",
                       color="account_type", title="Accounts by Type")
        st.plotly_chart(fig5, use_container_width=True)

        fig6 = px.bar(acc_df, x="account_type", y="total_balance",
                       color="account_type", title="Total Balance by Account Type")
        st.plotly_chart(fig6, use_container_width=True)

with tab3:
    left, right = st.columns(2)

    with left:
        st.subheader("Customers by City")
        city_df = analytics.get_customer_city_distribution()
        fig7 = px.bar(city_df, x="city", y="num_customers", color="city")
        st.plotly_chart(fig7, use_container_width=True)

    with right:
        st.subheader("Top Customers by Balance")
        top_n = st.number_input("Show top N", min_value=5, max_value=50, value=10)
        top_df = analytics.get_top_customers_by_balance(int(top_n))
        st.dataframe(top_df, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Flagged / Suspicious Transactions")
    st.caption("Rule-based flags: large debits (>₹40,000) and abnormal-amount outliers. "
               "Replace with a proper fraud model for production use.")
    limit = st.slider("Number of records", min_value=10, max_value=200, value=50, step=10)
    flagged_df = analytics.get_flagged_transactions(limit)
    if flagged_df.empty:
        st.success("No flagged transactions found.")
    else:
        st.dataframe(flagged_df, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("Search Customer")
    name = st.text_input("Enter customer name (partial match allowed)")
    if name:
        result_df = analytics.search_customer(name)
        if result_df.empty:
            st.warning("No matching customers found.")
        else:
            st.dataframe(result_df, use_container_width=True, hide_index=True)

st.divider()
st.caption("Digital Banking Analytics Platform — base project. Data is synthetically generated for demo purposes.")

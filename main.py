import streamlit as st
import pandas as pd

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Dairy Farm Management", layout="wide")

# ----------------------------
# GOOGLE SHEET IDS FROM SECRETS
# ----------------------------
INVESTMENT_SHEET_ID = st.secrets["sheets"]["INVESTMENT_SHEET_ID"]
MILK_DIS_M_SHEET_ID = st.secrets["sheets"]["MILK_DIS_M_SHEET_ID"]
MILK_DIS_E_SHEET_ID = st.secrets["sheets"]["MILK_DIS_E_SHEET_ID"]
EXPENSE_SHEET_ID = st.secrets["sheets"]["EXPENSE_SHEET_ID"]
COW_LOG_SHEET_ID = st.secrets["sheets"]["COW_LOG_SHEET_ID"]
PAYMENT_SHEET_ID = st.secrets["sheets"]["PAYMENT_SHEET_ID"]

# ----------------------------
# SHEET NAMES & URLs
# ----------------------------
INVESTMENT_CSV_URL = f"https://docs.google.com/spreadsheets/d/{INVESTMENT_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=investment"
MILK_DIS_M_CSV_URL = f"https://docs.google.com/spreadsheets/d/{MILK_DIS_M_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=morning"
MILK_DIS_E_CSV_URL = f"https://docs.google.com/spreadsheets/d/{MILK_DIS_E_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=evening"
EXPENSE_CSV_URL = f"https://docs.google.com/spreadsheets/d/{EXPENSE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=expense"
COW_LOG_CSV_URL = f"https://docs.google.com/spreadsheets/d/{COW_LOG_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=dailylog"
PAYMENT_CSV_URL = f"https://docs.google.com/spreadsheets/d/{PAYMENT_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=payment"

# ----------------------------
# DATA LOADING FUNCTION
# ----------------------------
@st.cache_data(ttl=600)
def load_csv(url, drop_cols=None):
    try:
        df = pd.read_csv(url)
        if drop_cols:
            df = df.drop(columns=[col for col in drop_cols if col in df.columns])
        return df
    except Exception as e:
        st.error(f"❌ Failed to load data from Google Sheet: {e}")
        return pd.DataFrame()

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def sum_numeric_columns(df, exclude_cols=None):
    """Sum all numeric columns except the excluded ones (used for milk totals)."""
    if df.empty:
        return 0
    if exclude_cols is None:
        exclude_cols = []
    numeric_cols = [col for col in df.columns if col not in exclude_cols]
    df_numeric = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    return df_numeric.sum().sum()

# ----------------------------
# SIDEBAR NAVIGATION
# ----------------------------
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["🏠 Dashboard", "Milking & Feeding", "Milk Distribution", "Expense", "Payments", "Investments"]
)

# ----------------------------
# DASHBOARD PAGE
# ----------------------------
if page == "🏠 Dashboard":
    st.title("📊 Dairy Farm Dashboard")
    st.caption("Overview of total performance and key farm metrics.")

    # Load all data
    df_expense = load_csv(EXPENSE_CSV_URL, drop_cols=["Timestamp"])
    df_invest = load_csv(INVESTMENT_CSV_URL, drop_cols=["Timestamp"])
    df_payment = load_csv(PAYMENT_CSV_URL, drop_cols=["Timestamp"])
    df_milk_m = load_csv(MILK_DIS_M_CSV_URL, drop_cols=["Timestamp"])
    df_milk_e = load_csv(MILK_DIS_E_CSV_URL, drop_cols=["Timestamp"])

    # ---- Totals ----
    total_expense = df_expense["Amount"].sum() if "Amount" in df_expense.columns else 0
    total_invest = df_invest["Amount"].sum() if "Amount" in df_invest.columns else 0
    total_payment = df_payment["Amount"].sum() if "Amount" in df_payment.columns else 0

    # Milk totals (sum all numeric columns except Timestamp & Date)
    total_milk_m = sum_numeric_columns(df_milk_m, exclude_cols=["Timestamp", "Date"])
    total_milk_e = sum_numeric_columns(df_milk_e, exclude_cols=["Timestamp", "Date"])
    total_milk = total_milk_m + total_milk_e

    # ---- KPIs ----
    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total Expenses", f"₹{total_expense:,.2f}")
    col2.metric("📈 Total Investment", f"₹{total_invest:,.2f}")
    col3.metric("💰 Total Payments", f"₹{total_payment:,.2f}")

    col4, col5 = st.columns(2)
    col4.metric("🥛 Total Milk Distributed", f"{total_milk:.2f} L")
    col5.metric("🌅 Morning Milk", f"{total_milk_m:.2f} L")
    col5.metric("🌇 Evening Milk", f"{total_milk_e:.2f} L")

    # ----------------------------
    # FUND AVAILABLE AT BIPIN KUMAR
    # ----------------------------
    
    # Filter data for Bipin Kumar
    bipin_invest = df_invest[df_invest["Paid To"].str.contains("Bipin Kumar", case=False, na=False)] if "Paid To" in df_invest.columns else pd.DataFrame()
    bipin_payment = df_payment[df_payment["Received By"].str.contains("Bipin Kumar", case=False, na=False)] if "Received By" in df_payment.columns else pd.DataFrame()
    bipin_expense = df_expense[df_expense["Expense By"].str.contains("Bipin Kumar", case=False, na=False)] if "Expense By" in df_expense.columns else pd.DataFrame()
    
    # Calculate totals
    total_invest_bipin = bipin_invest["Amount"].sum() if "Amount" in bipin_invest.columns else 0
    total_payment_bipin = bipin_payment["Amount"].sum() if "Amount" in bipin_payment.columns else 0
    total_expense_bipin = bipin_expense["Amount"].sum() if "Amount" in bipin_expense.columns else 0
    
    # Fund available at Bipin Kumar
    fund_bipin = total_invest_bipin + total_payment_bipin - total_expense_bipin
    
    st.divider()
    st.subheader("💼 Fund Summary")
    
    st.metric("Fund Available at Bipin Kumar", f"₹{fund_bipin:,.2f}")

    st.divider()
    st.subheader("📅 Recent Expense Entries")
    if not df_expense.empty:
        st.dataframe(df_expense.tail(5), use_container_width=True)
    else:
        st.info("No expense data yet.")

# ----------------------------
# MILKING & FEEDING PAGE
# ----------------------------
elif page == "Milking & Feeding":
    st.title("🐄 Milking & Feeding Log")
    st.caption("Daily cow log data including milk quantity, feed, and health details.")
    df = load_csv(COW_LOG_CSV_URL, drop_cols=["Timestamp"])
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No milking & feeding data available yet.")

# ----------------------------
# MILK DISTRIBUTION PAGE
# ----------------------------
elif page == "Milk Distribution":
    st.title("🥛 Milk Distribution")

    st.subheader("Morning Distribution")
    df_morning = load_csv(MILK_DIS_M_CSV_URL, drop_cols=["Timestamp"])
    if not df_morning.empty:
        st.dataframe(df_morning, use_container_width=True)
    else:
        st.info("No morning distribution data available.")

    st.subheader("Evening Distribution")
    df_evening = load_csv(MILK_DIS_E_CSV_URL, drop_cols=["Timestamp"])
    if not df_evening.empty:
        st.dataframe(df_evening, use_container_width=True)
    else:
        st.info("No evening distribution data available.")

# ----------------------------
# EXPENSE PAGE
# ----------------------------
elif page == "Expense":
    st.title("💸 Expense Tracker")
    df_expense = load_csv(EXPENSE_CSV_URL, drop_cols=["Timestamp"])
    if not df_expense.empty:
        st.dataframe(df_expense, use_container_width=True)
    else:
        st.info("No expense records found.")

# ----------------------------
# PAYMENTS PAGE
# ----------------------------
elif page == "Payments":
    st.title("💰 Payments Record")
    df_payment = load_csv(PAYMENT_CSV_URL, drop_cols=["Timestamp"])
    if not df_payment.empty:
        st.dataframe(df_payment, use_container_width=True)
    else:
        st.info("No payment records found.")

# ----------------------------
# INVESTMENTS PAGE
# ----------------------------
elif page == "Investments":
    st.title("📈 Investment Log")
    df_invest = load_csv(INVESTMENT_CSV_URL, drop_cols=["Timestamp"])
    if not df_invest.empty:
        st.dataframe(df_invest, use_container_width=True)
    else:
        st.info("No investment data found yet.")

# ----------------------------
# REFRESH BUTTON
# ----------------------------
if st.sidebar.button("🔁 Refresh"):
    st.rerun()

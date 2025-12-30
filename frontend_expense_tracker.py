import streamlit as st
import csv
import pandas as pd
from datetime import datetime

# -----------------------------
#  CSV SETTINGS
# -----------------------------
csv_file = "datarecord.csv"
headers = ["amount", "category", "date"]

# Create CSV if not exists
try:
    with open(csv_file, "x", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
except FileExistsError:
    pass


# -----------------------------
#  LOAD & SAVE FUNCTIONS
# -----------------------------
def load_data():
    try:
        return pd.read_csv(csv_file)
    except:
        return pd.DataFrame(columns=headers)


def save_data(amount, category, date):
    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([amount, category, date])


# -----------------------------
#  STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("💰 Simple & Elegant Expense Tracker")

st.divider()

data = load_data()

# -----------------------------
#  ADD EXPENSE
# -----------------------------
st.subheader("➕ Add New Expense")

with st.form("expense_form"):
    col1, col2 = st.columns(2)

    amount = col1.number_input("Amount Spent", min_value=0.0, format="%.2f")

    base_categories = [
        "transport", "groceries", "every day essentials",
        "clothes and selfcare", "essentials for home",
        "friends and fam needs", "food and snacks",
        "bills", "work needs"
    ]

    existing = data["category"].unique().tolist() if not data.empty else []
    categories = sorted(set(base_categories + existing))

    category = col2.selectbox("Category", categories)

    description = st.text_input("Description (optional)")

    submitted = st.form_submit_button("Save Expense")

    if submitted:
        if amount == 0:
            st.warning("Amount must be greater than 0.")
        else:
            today = str(datetime.now().date())
            save_data(amount, category, today)
            st.success("Expense added!")
            st.experimental_rerun()

# -----------------------------
#  TODAY'S SPENDING SUMMARY
# -----------------------------
st.divider()
st.subheader("📅 Today's Summary")

today = str(datetime.now().date())
today_data = data[data["date"] == today]

if not today_data.empty:
    today_data["amount"] = today_data["amount"].astype(float)

    total = today_data["amount"].sum()
    st.metric("Total Spent Today", f"₹ {total:.2f}")

    st.write("### Category Breakdown (Today)")
    cat_group = today_data.groupby("category")["amount"].sum()

    # Pie chart using Matplotlib + Streamlit
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.pie(cat_group.values, labels=cat_group.index, autopct="%1.1f%%")
    ax.axis("equal")
    st.pyplot(fig)

else:
    st.info("No expenses recorded today.")

# -----------------------------
#  FULL HISTORY + STREAMLIT GRAPHS
# -----------------------------
st.divider()
st.subheader("📊 Full Expense History")

if data.empty:
    st.info("No data available.")
else:
    data["amount"] = data["amount"].astype(float)

    st.dataframe(data, use_container_width=True)

    # Total spending by category
    st.write("### 📌 Spending by Category (All Time)")
    cat_sum = data.groupby("category")["amount"].sum()

    st.bar_chart(cat_sum)

    # Daily spending trend
    st.write("### 📅 Daily Spending Trend")
    daily_sum = data.groupby("date")["amount"].sum()

    st.line_chart(daily_sum)

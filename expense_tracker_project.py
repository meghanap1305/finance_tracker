import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import csv
from datetime import datetime
import os
import io

# ==========================================
# BACKEND LOGIC (Originally expense.py)
# ==========================================

st.set_page_config(page_title="Expense Tracker",layout="wide")
DEFAULT_CATEGORIES = [
    "transport", "groceries", "every day essentials",
    "clothes and other selfcare items", "essentials to home",
    "friends and fam needs", "food and snacks", "bills", 
    "work needs", "Other"
]

def log_expense(amount, category, brief_description):
    """
    Takes inputs from the frontend and saves them to the CSV.
    """
    date = datetime.now()
    today = str(date.date())

    try:
        with open("datarecord.csv", 'a', newline='') as f:
            write = csv.writer(f)
            # Check if file is empty to write headers
            if f.tell() == 0:
                write.writerow(["amount", "category", "date", "description"])
            
            write.writerow([amount, category, today, brief_description])
            return "Expense successfully added!"
            
    except PermissionError:
        return "Error: File is open in Excel. Close it and try again."
    except Exception as e:
        return f"Unexpected error: {e}"

def get_total_today():
    """Calculates total spent today"""
    total_amnt_spent_today = 0
    today = str(datetime.now().date())
    
    try:
        with open("datarecord.csv", 'r') as file:
            l = csv.DictReader(file)
            for i in l:
                if i["date"] == today:
                    total_amnt_spent_today += float(i["amount"])
        return total_amnt_spent_today
    except FileNotFoundError:
        return 0

def get_daily_breakdown():
    category_totals={}
    today=str(datetime.now().date())
    try:
        with open("datarecord.csv","r")as f:
            r=csv.DictReader(f)
            for row in r:
                if row["date"]==today:
                    cat=row["category"]
                    amount=float(row["amount"])
                    if cat in category_totals:
                        category_totals[cat]+=amount 
                    else:
                        category_totals[cat]=amount
        return category_totals
    except FileNotFoundError:
        return {}

def get_expense_trends():
    trends={}
    try:
        with open("datarecord.csv","r")as f:
            r=csv.DictReader(f)
            for row in r:
                dates=row["date"]
                amount=float(row["amount"])
                if dates not in trends.keys():
                    trends[dates]=amount
                else:
                    trends[dates]+=amount
        sorted_trends=dict(sorted(trends.items()))
        return sorted_trends
    except FileNotFoundError:
        return {}

# ==========================================
# FRONTEND UI (Originally frontend_byme.py)
# ==========================================

st.title("💰 Expense Tracker 💰")
st.header("Turn chaos into clarity--plan your expenses effortlessly")

amount=st.number_input("Enter the amount spent", min_value=10.0, step=10.0)
selected_category=st.selectbox("Select Category", DEFAULT_CATEGORIES)

current_categories=DEFAULT_CATEGORIES.copy()
if os.path.exists("datarecord.csv"):
    try:
        df_cat_check = pd.read_csv("datarecord.csv")
        if 'category' in df_cat_check.columns:
            # Get unique categories from file and add to default list
            existing_cats = df_cat_check['category'].dropna().unique().tolist()
            # Merge lists and remove duplicates
            current_categories = list(set(current_categories + existing_cats))
    except Exception:
        pass # If file read fails, just use default
if selected_category=="Other":
    category=st.text_input("Type ur category here")
else:
    category=selected_category

brief=st.text_input("Brief Description")

if st.button("Add Expenses"):
    if amount>0 and category and brief:
        # Calls the function directly (no 'expense.' prefix needed)
        result_msg=log_expense(amount, category, brief)
        if "Error" in result_msg:
            st.error(result_msg)
        else:
            st.success(f"Added:{category}   {amount}")
    else:
        st.warning("Please fill out all the fields")

st.divider()
col1,col2=st.columns(2)

with col1:
    st.subheader("Today's Overview")

    current_total=get_total_today()
    st.metric("Total spent today",f"{current_total}")

    breakdown_data=get_daily_breakdown()
    if breakdown_data:
        #prepares data for plotting
        labels=list(breakdown_data.keys())
        size=list(breakdown_data.values())
        fig,ax=plt.subplots()#creates the fig and aixs
        ax.pie(size,labels=labels,autopct='%1.2f%%',startangle=90)
        ax.axis('equal')#ensures it is a circle

        st.pyplot(fig)# to display the plot in streamlit
    else:
        st.info("No expenses recorded today yet")

with col2:
    st.subheader("Spending Trends")
    trend_data=get_expense_trends()
    if trend_data:
        #converts dictionary to pandas data frame which is better to deal with time frames
        df_trend=pd.DataFrame(list(trend_data.items()), columns=['Date','Amount'])
        #converts 'Date' column to datetime objects 
        df_trend['Date']=pd.to_datetime(df_trend['Date'])
        #set date as index
        df_trend.set_index('Date',inplace=True)
        st.line_chart(df_trend)
    else:
        st.info("Not enough data for trends")

st.divider()
st.subheader("📝 Data Log & History 📝")
try:
    if os.path.exists("datarecord.csv"):
        df_all=pd.read_csv("datarecord.csv")

        st.dataframe(
            df_all.sort_values(by="date",ascending=False),#shows the latest entry first
            use_container_width='stretch',
            hide_index='stretch'
        )
        csv_data=df_all.to_csv(index=False).encode('utf-8')#so since i used pandas to convert it to a datfram it just returns binary values,to convert it into text encode binary values to text
        st.download_button(label="Download Data as CSV",data=csv_data,file_name="my_expenses.csv",mime="text/csv")
        buffer =io.BytesIO()

        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_all.to_excel(writer, index=False, sheet_name='Expenses')
        st.download_button(label="Download data as Excel",data=buffer.getvalue(),file_name="my_expenses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")#mime part is specific to excel file it basically tells the computer that the file being downloaded is an excel file,not a binary
    else:
        st.info("No data found yet. Add an expense to see the log")
except Exception as e:
    st.error(f"Could not load data log: {e}")

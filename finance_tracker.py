# Name: FinVision 💰 - Professional Finance Analytics Dashboard

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Configure page
st.set_page_config(
    page_title="FinVision - Personal Finance Dashboard by Aqsaa Qaazi",
    page_icon="💰",
    layout="wide"
)
# Custom CSS for animations and hover effects
st.markdown("""
<style>
@keyframes fadeIn {
  from {opacity: 0;}
  to {opacity: 1;}
}

.card {
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin: 10px 0;
    animation: fadeIn 0.5s ease-in;
    transition: transform 0.2s;
    background: white;
}

.card:hover {
    transform: translateY(-5px);
}

.stButton>button {
    transition: all 0.3s ease;
    border: 2px solid #4CAF50;
}

.stButton>button:hover {
    background: #4CAF50 !important;
    color: white !important;
    border: 2px solid #45a049;
}

.fade-in {
    animation: fadeIn 1s;
}
</style>
""", unsafe_allow_html=True)

import os

# Check if file exists before reading
if os.path.exists('finance_data.csv'):
    st.session_state.transactions = pd.read_csv('finance_data.csv')
else:
    st.warning("No transaction history found. Add a transaction first!")
    st.session_state.transactions = pd.DataFrame(columns=["Date", "Category", "Amount"])


# Initialize session state for data
if os.path.exists('finance_data.csv') and os.path.getsize('finance_data.csv') > 0:
    try:
        st.session_state.transactions = pd.read_csv('finance_data.csv')
    except pd.errors.EmptyDataError:
        st.session_state.transactions = pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Description"])
else:
    st.session_state.transactions = pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Description"])

# Save to CSV function
def save_data():
    st.session_state.transactions.to_csv('finance_data.csv', index=False)

# Main dashboard header
st.markdown('<h1 class="fade-in">💰 FinVision - Financial Analytics</h1>', unsafe_allow_html=True)

# Input Section with Card Layout
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([2,2,2,3])
    
    with col1:
        date = st.date_input("📅 Date", datetime.today())
    with col2:
        category = st.selectbox("🏷 Category", 
            ['Food', 'Transport', 'Housing', 'Entertainment', 'Salary', 'Educational Fees', 'Rent','Other'])
    with col3:
        amount = st.number_input("💵 Amount", min_value=0.0, step=10.0)
    with col4:
        description = st.text_input("📝 Description")
        transaction_type = st.radio("Type", ['Income', 'Expense'], horizontal=True)
    
    if st.button("➕ Add Transaction", type="primary"):
        if amount > 0 and description:
            new_entry = {
                'Date': date.strftime("%Y-%m-%d"),
                'Type': transaction_type,
                'Category': category,
                'Amount': amount if transaction_type == 'Income' else -amount,
                'Description': description
            }
            st.session_state.transactions = pd.concat(
                [st.session_state.transactions, pd.DataFrame([new_entry])],
                ignore_index=True
            )
            save_data()
            st.success("Transaction added successfully!")
        else:
            st.error("Please fill all fields correctly")
    st.markdown('</div>', unsafe_allow_html=True)

# Dashboard Metrics
with st.container():
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    total_income = st.session_state.transactions[st.session_state.transactions['Amount'] > 0]['Amount'].sum()
    total_expense = abs(st.session_state.transactions[st.session_state.transactions['Amount'] < 0]['Amount'].sum())
    balance = total_income - total_expense
    
    with col1:
        st.metric("💰 Total Balance", f"${balance:,.2f}", delta_color="off")
    with col2:
        st.metric("📈 Total Income", f"${total_income:,.2f}" )
                                                        # delta="+5% vs last month"
    with col3:
        st.metric("📉 Total Expenses", f"${total_expense:,.2f}" )
                                                            # delta="-3% vs last month"
    st.markdown('</div>', unsafe_allow_html=True)

# Visualizations
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
        st.subheader("📊 Expense Distribution")
        expense_df = st.session_state.transactions[st.session_state.transactions['Type'] == 'Expense']
        fig = px.pie(expense_df, values='Amount', names='Category', hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
        st.subheader("📈 Monthly Trend")
        monthly_data = st.session_state.transactions.copy()
        monthly_data['Month'] = pd.to_datetime(monthly_data['Date']).dt.to_period('M')
        monthly_summary = monthly_data.groupby('Month')['Amount'].sum().reset_index()
        monthly_summary['Month'] = monthly_summary['Month'].astype(str)
        fig = px.bar(monthly_summary, x='Month', y='Amount', 
                    color_discrete_sequence=['#4CAF50'])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Transaction History
with st.container():
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.subheader("📋 Transaction History")
    
    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        filter_type = st.multiselect("Filter by Type", ['Income', 'Expense'], default=['Income', 'Expense'])
    with col2:
        filter_category = st.multiselect("Filter by Category", 
            st.session_state.transactions['Category'].unique())
    
    filtered_data = st.session_state.transactions.copy()
    if filter_type:
        filtered_data = filtered_data[filtered_data['Type'].isin(filter_type)]
    if filter_category:
        filtered_data = filtered_data[filtered_data['Category'].isin(filter_category)]
    
    # Style DataFrame
    def color_amount(val):
        color = 'green' if val > 0 else 'red'
        return f'color: {color}'
    
    st.dataframe(
        filtered_data.style.applymap(color_amount, subset=['Amount'])
        .format({'Amount': '${0:,.2f}'}),
        height=300,
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)



from dotenv import load_dotenv
load_dotenv()          # ← this makes sure ALL your .env vars are read

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import plotly.express as px
import os


from database import Database
from portfolio import PortfolioAnalyzer
from transactions import TransactionClassifier
from risk import RiskAnalyzer
from advisor import BudgetAdvisor



# Initialize database and components
db = Database()
portfolio_analyzer = PortfolioAnalyzer(db)
transaction_classifier = TransactionClassifier(db)
risk_analyzer = RiskAnalyzer(db)
budget_advisor = BudgetAdvisor(db)

# Page config
st.set_page_config(
    page_title="AI-Powered Financial Copilot",
    page_icon="💰",
    layout="wide"
)

# Sidebar navigation
with st.sidebar:
    st.title("Financial Copilot")
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Portfolio", "Transactions", "Risk", "Advisor"],
        icons=["house", "graph-up", "credit-card", "exclamation-triangle", "chat-dots"],
        menu_icon="cast",
        default_index=0,
    )

# User session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'monthly_income' not in st.session_state:
    st.session_state.monthly_income = None

# Home page
if selected == "Home":
    st.title("Welcome to AI-Powered Financial Copilot")
    st.write("Your personal financial assistant powered by AI")
    
    # User registration
    with st.form("user_registration"):
        st.subheader("Get Started")
        username = st.text_input("Enter your name")
        monthly_income = st.number_input("Enter your monthly income ($)", min_value=0.0)
        submit = st.form_submit_button("Start")
        
        if submit:
            user_id = db.add_user(username, monthly_income)
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.monthly_income = monthly_income
                st.success(f"Welcome, {username}!")
            else:
                st.error("Error creating user profile. Please try again.")

# Portfolio page
elif selected == "Portfolio":
    st.title("Portfolio Analyzer")
    
    if not st.session_state.user_id:
        st.warning("Please complete registration on the Home page first.")
    else:
        # Add new stock
        with st.form("add_stock"):
            st.subheader("Add Stock to Portfolio")
            ticker = st.text_input("Stock Ticker (e.g., AAPL)")
            quantity = st.number_input("Quantity", min_value=1)
            purchase_price = st.number_input("Purchase Price ($)", min_value=0.0)
            submit = st.form_submit_button("Add Stock")
            
            if submit and ticker:
                db.save_portfolio(st.session_state.user_id, ticker, quantity, purchase_price)
                st.success(f"Added {quantity} shares of {ticker} to portfolio")
        
        # Display portfolio
        portfolio_df = db.get_user_portfolio(st.session_state.user_id)
        if not portfolio_df.empty:
            portfolio_value = portfolio_analyzer.calculate_portfolio_value(portfolio_df)
            summary = portfolio_analyzer.get_portfolio_summary(portfolio_value)
            
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Investment", f"${summary['total_investment']:.2f}")
            with col2:
                st.metric("Current Value", f"${summary['current_value']:.2f}")
            with col3:
                st.metric("Gain/Loss", f"${summary['total_gain_loss']:.2f}")
            with col4:
                st.metric("Return", f"{summary['total_gain_loss_pct']:.1f}%")
            
            # Display charts
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(portfolio_analyzer.plot_portfolio_allocation(portfolio_value))
            with col2:
                st.plotly_chart(portfolio_analyzer.plot_price_trends(portfolio_df))
            
            # Display detailed portfolio table
            st.subheader("Portfolio Details")
            st.dataframe(portfolio_value)
        else:
            st.info("No stocks in portfolio. Add some stocks to get started!")

# Transactions page
elif selected == "Transactions":
    st.title("Transaction Classifier")
    
    if not st.session_state.user_id:
        st.warning("Please complete registration on the Home page first.")
    else:
        # File upload
        uploaded_file = st.file_uploader("Upload Transaction CSV", type=['csv'])
        
        if uploaded_file is not None:
            try:
                transactions_df = pd.read_csv(uploaded_file)
                processed_df = transaction_classifier.process_transactions(transactions_df)
                
                # Save to database
                db.save_transactions(st.session_state.user_id, processed_df)
                
                # Display results
                st.subheader("Transaction Analysis")
                
                # Display spending breakdown chart
                st.plotly_chart(transaction_classifier.plot_spending_breakdown(processed_df))
                
                # Display category summary
                st.subheader("Category Summary")
                summary = transaction_classifier.get_category_summary(processed_df)
                st.dataframe(summary)
                
                # Display raw transactions
                st.subheader("Processed Transactions")
                st.dataframe(processed_df)
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

# Risk page
elif selected == "Risk":
    st.title("Financial Risk Detector")
    
    if not st.session_state.user_id:
        st.warning("Please complete registration on the Home page first.")
    else:
        transactions_df = db.get_user_transactions(st.session_state.user_id)
        
        if not transactions_df.empty:
            risk_analysis = risk_analyzer.calculate_risk_level(
                st.session_state.monthly_income,
                transactions_df
            )
            
            # Display risk level
            st.subheader("Risk Assessment")
            risk_color = {
                'Low': 'green',
                'Medium': 'orange',
                'High': 'red'
            }
            st.markdown(f"### Risk Level: :{risk_color[risk_analysis['risk_level']]}[{risk_analysis['risk_level']}]")
            
            # Display reason
            st.write("**Analysis:**", risk_analysis['reason'])
            
            # Display recommendations
            st.subheader("Recommendations")
            recommendations = risk_analyzer.get_risk_recommendations(risk_analysis)
            for rec in recommendations:
                st.write(f"- {rec}")
            
            # Save risk analysis
            db.save_risk_analysis(
                st.session_state.user_id,
                risk_analysis['risk_level'],
                risk_analysis['savings_buffer']
            )
        else:
            st.info("Upload transactions to get a risk assessment.")

# Advisor page
elif selected == "Advisor":
    st.title("Budget Advisor")

    
    
    if not st.session_state.user_id:
        st.warning("Please complete registration on the Home page first.")
    else:
        transactions_df = db.get_user_transactions(st.session_state.user_id)
        
        if not transactions_df.empty:
            # Get latest risk analysis
            risk_analysis = db.get_latest_risk_analysis(st.session_state.user_id)
            print("TYPE CHECK →", type(risk_analysis))
            risk_level = risk_analysis['risk_level'] if (risk_analysis is not None and not getattr(risk_analysis, 'empty', False)) else 'Medium'
            
            # Generate advice
            advice = budget_advisor.generate_advice(
                st.session_state.monthly_income,
                transactions_df,
                risk_level
            )
            
            # Display advice
            st.subheader("Personalized Financial Advice")
            st.write(advice)
            
            # Display spending insights
            st.subheader("Spending Insights")
            insights = budget_advisor.get_spending_insights(transactions_df)
            for insight in insights:
                st.write(f"- {insight}")

            # Show financial chatbot
            budget_advisor.financial_chatbot()
        else:
            st.info("Upload transactions to get personalized financial advice.")

# Add footer
st.markdown("---")
st.markdown("By YASHI ") 

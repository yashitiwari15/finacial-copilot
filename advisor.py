from dotenv import load_dotenv
load_dotenv()

from langchain.prompts import PromptTemplate
import pandas as pd
import os
import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from together import Together


class BudgetAdvisor:
    def __init__(self, db):
        self.db = db

        # Initialize Together client for non-streaming tasks
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

        self.advice_prompt = PromptTemplate(
            input_variables=["income", "expenses", "category_breakdown", "risk_level"],
            template="""As a friendly financial advisor, analyze the following financial data and provide personalized budgeting advice:

Monthly Income: ${income}
Total Monthly Expenses: ${expenses}
Expense Categories: {category_breakdown}
Current Risk Level: {risk_level}

Please provide:
1. A brief analysis of the spending patterns
2. 2-3 specific, actionable recommendations for improving financial health
3. A friendly, encouraging message about financial goals

Keep the tone conversational and supportive. Focus on practical, achievable steps."""
        )

    def generate_advice(self, monthly_income, transactions_df, risk_level):
        if transactions_df.empty:
            return "Please upload transaction data to receive personalized financial advice."

        total_expenses = transactions_df['amount'].sum()
        category_totals = transactions_df.groupby('category')['amount'].sum()
        category_percentages = (category_totals / total_expenses * 100).round(1)

        category_breakdown = "\n".join([
            f"{category}: ${amount:.2f} ({percentage}%)"
            for category, (amount, percentage) in zip(
                category_percentages.index,
                zip(category_totals, category_percentages)
            )
        ])

        prompt_text = self.advice_prompt.format(
            income=monthly_income,
            expenses=total_expenses,
            category_breakdown=category_breakdown,
            risk_level=risk_level
        )

        try:
            response = self.client.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Unable to generate advice at this time. Error: {str(e)}"

    def get_spending_insights(self, transactions_df):
        if transactions_df.empty:
            return []

        insights = []
        category_stats = transactions_df.groupby('category').agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)

        highest_category = category_stats[('amount', 'sum')].idxmax()
        highest_amount = category_stats[('amount', 'sum')].max()
        insights.append(f"Highest spending category: {highest_category} (${highest_amount:.2f})")

        most_frequent = category_stats[('amount', 'count')].idxmax()
        frequency = category_stats[('amount', 'count')].max()
        insights.append(f"Most frequent category: {most_frequent} ({frequency} transactions)")

        avg_transaction = transactions_df['amount'].mean()
        insights.append(f"Average transaction amount: ${avg_transaction:.2f}")

        return insights

    def financial_chatbot(self):
        st.markdown("""
            <style>
            .stChatMessage {
                background-color: #f0f4fa;
                padding: 12px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
            .stChatMessage, .stChatMessage * {
               color: black !important;
            }
            .stChatMessage.user {
                background-color: #dbe9ff;
            }
            .stChatMessage.assistant {
                background-color: #ffffff;
                border-left: 5px solid #0072ff;
            }
            .avatar-container {
                display: flex;
                align-items: center;
            }
            .avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .typing {
                font-style: italic;
                color: gray;
                margin-left: 10px;
            }
            </style>
        """, unsafe_allow_html=True)

        st.subheader("Talk to CashGPT")

        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = [
                {
                    "role": "system",
                    "content": (
                        "You are CashGPT, a professional and friendly AI financial advisor. "
                        "You only answer questions related to personal finance, budgeting, saving, investing, risk analysis, or financial planning. "
                        "If a user asks anything not related to finance (like skincare, entertainment, cooking, personal opinions, etc.), reply strictly with: "
                        "'I'm here to help with financial topics. Could you ask me something about budgeting, saving, or investing?'"
                    )
                }
            ]

        # Show chat history with avatars
        for msg in st.session_state.chat_history:
            if msg["role"] == "system":
                continue
            role = msg["role"]
            avatar = "https://cdn-icons-png.flaticon.com/512/4333/4333609.png" if role == "user" else "https://cdn-icons-png.flaticon.com/512/10262/10262690.png"
            with st.chat_message(role):
                st.markdown(f"""
                    <div class='avatar-container'>
                        <img src="{avatar}" class="avatar"/>
                        <div class='stChatMessage {role}'>{msg["content"]}</div>
                    </div>
                """, unsafe_allow_html=True)

        # Input + Response
        user_input = st.chat_input("Ask me anything about your finances...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                typing_placeholder = st.empty()
                typing_placeholder.markdown("<span class='typing'>CashGPT is thinking...</span>", unsafe_allow_html=True)

                try:
                    response = self.client.chat.completions.create(
                        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                        messages=st.session_state.chat_history,
                        temperature=0.7,
                        max_tokens=300
                    )
                    assistant_reply = response.choices[0].message.content
                    typing_placeholder.empty()
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                    st.markdown(assistant_reply)
                except Exception as e:
                    typing_placeholder.empty()
                    st.error(f"Error generating response: {e}")


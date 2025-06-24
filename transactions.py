import pandas as pd
import re
import plotly.express as px
from langchain.prompts import PromptTemplate
from langchain.llms import HuggingFaceHub
from langchain.chains import LLMChain
import os

class TransactionClassifier:
    def __init__(self, db):
        self.db = db
        self.category_patterns = {
            'Food': r'(restaurant|cafe|food|grocery|supermarket|dining)',
            'Travel': r'(uber|lyft|taxi|flight|hotel|airbnb|travel)',
            'Shopping': r'(amazon|walmart|target|shop|store|mall)',
            'Bills': r'(electric|water|gas|internet|phone|utility)',
            'Entertainment': r'(netflix|spotify|hulu|movie|theater)',
            'Healthcare': r'(pharmacy|doctor|hospital|medical)',
            'Education': r'(school|university|course|book|education)',
            'Transportation': r'(gas|fuel|car|bus|train|metro)',
            'Other': r'.*'
        }
        

        self.llm = HuggingFaceHub(
            repo_id="google/flan-t5-xl",
            model_kwargs={"temperature": 0.5, "max_new_tokens": 100},
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
        )
        print("✅ LLM initialized:", self.llm)
        self.classification_prompt = PromptTemplate(
            input_variables=["merchant"],
            template="""Given the merchant name '{merchant}', classify it into one of these categories:
            Food, Travel, Shopping, Bills, Entertainment, Healthcare, Education, Transportation, or Other.
            Return only the category name."""
        )
        self.classification_chain = LLMChain(llm=self.llm, prompt=self.classification_prompt)

    def classify_transaction(self, merchant):
        # Try regex patterns first
        for category, pattern in self.category_patterns.items():
            if re.search(pattern, merchant.lower()):
                return category
        
        # If no match, use LLM
        try:
            category = self.classification_chain.run(merchant=merchant)
            return category.strip()
        except:
            return 'Other'

    def process_transactions(self, transactions_df):
        if transactions_df.empty:
            return pd.DataFrame()

        # Ensure required columns exist
        required_columns = ['date', 'amount', 'merchant']
        if not all(col in transactions_df.columns for col in required_columns):
            raise ValueError("CSV must contain 'date', 'amount', and 'merchant' columns")

        # Add category column
        transactions_df['category'] = transactions_df['merchant'].apply(self.classify_transaction)
        return transactions_df

    def plot_spending_breakdown(self, transactions_df):
        if transactions_df.empty:
            return None

        category_totals = transactions_df.groupby('category')['amount'].sum().reset_index()
        fig = px.bar(
            category_totals,
            x='category',
            y='amount',
            title='Spending by Category',
            labels={'amount': 'Total Amount ($)', 'category': 'Category'}
        )
        return fig

    def get_category_summary(self, transactions_df):
        if transactions_df.empty:
            return pd.DataFrame()

        summary = transactions_df.groupby('category').agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)
        
        summary.columns = ['total_amount', 'transaction_count', 'average_amount']
        return summary.reset_index() 
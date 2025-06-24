import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

class PortfolioAnalyzer:
    def __init__(self, db):
        self.db = db

    def get_stock_data(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1mo")
            return {
                'current_price': info.get('currentPrice', 0),
                'history': hist
            }
        except (json.JSONDecodeError, Exception):
            return {
                'current_price': 0,
                'history': None
            }

    def calculate_portfolio_value(self, portfolio_df):
        if portfolio_df.empty:
            return pd.DataFrame()

        portfolio_data = []
        for _, row in portfolio_df.iterrows():
            stock_data = self.get_stock_data(row['ticker'])
            current_value = stock_data['current_price'] * row['quantity']
            initial_value = row['purchase_price'] * row['quantity']
            gain_loss = current_value - initial_value
            gain_loss_pct = (gain_loss / initial_value) * 100

            portfolio_data.append({
                'ticker': row['ticker'],
                'quantity': row['quantity'],
                'purchase_price': row['purchase_price'],
                'current_price': stock_data['current_price'],
                'initial_value': initial_value,
                'current_value': current_value,
                'gain_loss': gain_loss,
                'gain_loss_pct': gain_loss_pct
            })

        return pd.DataFrame(portfolio_data)

    def plot_portfolio_allocation(self, portfolio_df):
        if portfolio_df.empty:
            return None

        fig = px.pie(
            portfolio_df,
            values='current_value',
            names='ticker',
            title='Portfolio Allocation',
            hole=0.3
        )
        return fig

    def plot_price_trends(self, portfolio_df):
        if portfolio_df.empty:
            return None

        fig = go.Figure()
        for _, row in portfolio_df.iterrows():
            stock = yf.Ticker(row['ticker'])
            hist = stock.history(period="1mo")
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                name=row['ticker']
            ))

        fig.update_layout(
            title='Stock Price Trends (Last Month)',
            xaxis_title='Date',
            yaxis_title='Price',
            hovermode='x unified'
        )
        return fig

    def get_portfolio_summary(self, portfolio_df):
        if portfolio_df.empty:
            return {
                'total_investment': 0,
                'current_value': 0,
                'total_gain_loss': 0,
                'total_gain_loss_pct': 0
            }

        total_investment = portfolio_df['initial_value'].sum()
        current_value = portfolio_df['current_value'].sum()
        total_gain_loss = current_value - total_investment
        total_gain_loss_pct = (total_gain_loss / total_investment) * 100 if total_investment > 0 else 0

        return {
            'total_investment': total_investment,
            'current_value': current_value,
            'total_gain_loss': total_gain_loss,
            'total_gain_loss_pct': total_gain_loss_pct
        } 
import sqlite3
import pandas as pd
from datetime import datetime

class Database:
    def __init__(self, db_name="financial_copilot.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            monthly_income REAL,
            risk_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TIMESTAMP,
            amount REAL,
            merchant TEXT,
            category TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # Create portfolio table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ticker TEXT,
            quantity INTEGER,
            purchase_price REAL,
            purchase_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # Create risk_analysis table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            risk_level TEXT,
            analysis_date TIMESTAMP,
            savings_buffer REAL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        conn.commit()
        conn.close()

    def add_user(self, username, monthly_income):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, monthly_income) VALUES (?, ?)",
                (username, monthly_income)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def save_transactions(self, user_id, transactions_df):
        conn = self.get_connection()
        transactions_df['user_id'] = user_id
        transactions_df.to_sql('transactions', conn, if_exists='append', index=False)
        conn.close()

    def get_user_transactions(self, user_id):
        conn = self.get_connection()
        query = f"SELECT * FROM transactions WHERE user_id = {user_id}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def save_portfolio(self, user_id, ticker, quantity, purchase_price):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO portfolio (user_id, ticker, quantity, purchase_price, purchase_date) VALUES (?, ?, ?, ?, ?)",
            (user_id, ticker, quantity, purchase_price, datetime.now())
        )
        conn.commit()
        conn.close()

    def get_user_portfolio(self, user_id):
        conn = self.get_connection()
        query = f"SELECT * FROM portfolio WHERE user_id = {user_id}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def save_risk_analysis(self, user_id, risk_level, savings_buffer):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO risk_analysis (user_id, risk_level, analysis_date, savings_buffer) VALUES (?, ?, ?, ?)",
            (user_id, risk_level, datetime.now(), savings_buffer)
        )
        conn.commit()
        conn.close()

    def get_latest_risk_analysis(self, user_id):
        conn = self.get_connection()
        query = f"""
        SELECT * FROM risk_analysis 
        WHERE user_id = {user_id} 
        ORDER BY analysis_date DESC 
        LIMIT 1
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.iloc[0] if not df.empty else None 
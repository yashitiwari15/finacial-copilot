# AI-Powered Financial Copilot

A smart personal finance assistant built using Streamlit, LangChain, yFinance, Hugging Face, and Together AI. The application enables users to analyze investment portfolios, categorize transactions, evaluate financial risk, and receive personalized budgeting recommendations through an LLM-powered chatbot interface.

## Features

1. **Portfolio Analyzer**
   - Track stock investments
   - View live stock prices and performance
   - Interactive portfolio allocation charts
   - Real-time gain/loss calculations

2. **Transaction Classifier**
   - Upload bank/UPI statements
   - Automatic transaction categorization
   - Spending breakdown visualization
   - Category-wise expense analysis

3. **Financial Risk Detector**
   - Risk level assessment
   - Personalized recommendations
   - Emergency fund suggestions
   - Spending pattern analysis

4. **Budget Advisor**
   - AI-powered financial chatbot
   - Personalized budgeting tips
   - Spending insights
   - Actionable recommendations

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd financial-copilot
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Follow the on-screen instructions:
   - Register with your name and monthly income
   - Upload transaction data using the sample CSV format
   - Add stocks to your portfolio
   - Get personalized financial advice

## Sample Data

A sample transaction CSV file (`sample_transactions.csv`) is included for testing. The file contains example transactions with the following columns:
- date: Transaction date (YYYY-MM-DD)
- amount: Transaction amount
- merchant: Merchant name

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for stock data and AI features

## Contributing

Feel free to submit issues and enhancement requests! 

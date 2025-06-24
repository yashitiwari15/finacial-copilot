import pandas as pd
import numpy as np

class RiskAnalyzer:
    def __init__(self, db):
        self.db = db

    def calculate_risk_level(self, monthly_income, transactions_df):
        if transactions_df.empty:
            return {
                'risk_level': 'Medium',
                'reason': 'No transaction data available',
                'savings_buffer': monthly_income * 0.3
            }

        # Calculate monthly expenses
        monthly_expenses = transactions_df['amount'].sum()
        
        # Calculate expense ratios
        expense_ratio = monthly_expenses / monthly_income if monthly_income > 0 else float('inf')
        
        # Calculate category ratios
        category_totals = transactions_df.groupby('category')['amount'].sum()
        category_ratios = category_totals / monthly_income if monthly_income > 0 else pd.Series(0)
        
        # Risk assessment rules
        risk_factors = []
        
        # Rule 1: Overall expense ratio
        if expense_ratio > 0.9:
            risk_factors.append("Expenses exceed 90% of income")
        elif expense_ratio > 0.7:
            risk_factors.append("Expenses exceed 70% of income")
        
        # Rule 2: Category-specific ratios
        if category_ratios.get('Food', 0) > 0.3:
            risk_factors.append("Food expenses exceed 30% of income")
        if category_ratios.get('Entertainment', 0) > 0.2:
            risk_factors.append("Entertainment expenses exceed 20% of income")
        if category_ratios.get('Shopping', 0) > 0.25:
            risk_factors.append("Shopping expenses exceed 25% of income")
        
        # Rule 3: Emergency fund check
        savings_buffer = monthly_income * 0.3  # Default to 3 months of income
        
        # Determine risk level
        if len(risk_factors) >= 3 or expense_ratio > 0.9:
            risk_level = 'High'
            savings_buffer = monthly_income * 0.5  # 5 months of income
        elif len(risk_factors) >= 1 or expense_ratio > 0.7:
            risk_level = 'Medium'
            savings_buffer = monthly_income * 0.4  # 4 months of income
        else:
            risk_level = 'Low'
            savings_buffer = monthly_income * 0.3  # 3 months of income
        
        return {
            'risk_level': risk_level,
            'reason': '; '.join(risk_factors) if risk_factors else "Good financial health",
            'savings_buffer': savings_buffer,
            'expense_ratio': expense_ratio,
            'category_ratios': category_ratios.to_dict()
        }

    def get_risk_recommendations(self, risk_analysis):
        recommendations = []
        
        if risk_analysis['risk_level'] == 'High':
            recommendations.extend([
                "Immediately reduce non-essential expenses",
                f"Build emergency fund of ${risk_analysis['savings_buffer']:.2f}",
                "Consider debt consolidation if applicable",
                "Create strict budget and track expenses daily"
            ])
        elif risk_analysis['risk_level'] == 'Medium':
            recommendations.extend([
                "Review and reduce discretionary spending",
                f"Build emergency fund of ${risk_analysis['savings_buffer']:.2f}",
                "Set up automatic savings transfers",
                "Monitor expenses weekly"
            ])
        else:
            recommendations.extend([
                f"Maintain emergency fund of ${risk_analysis['savings_buffer']:.2f}",
                "Continue current saving habits",
                "Consider investment opportunities",
                "Review budget monthly"
            ])
        
        return recommendations 
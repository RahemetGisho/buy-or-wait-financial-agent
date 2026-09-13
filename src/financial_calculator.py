"""Financial calculation and forecasting engine."""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class FinancialCalculator:
    """Calculates 90-day cash flow forecasts and safe payment amounts."""
    
    def __init__(self, profile: Dict, exchange_rates_df: pd.DataFrame):
        self.profile = profile
        self.exchange_rates_df = exchange_rates_df
        self.user_currency = profile['home_currency']
        self.current_balance = float(profile['current_available_balance'])
        self.minimum_balance = float(profile['minimum_balance_to_keep'])
    
    def forecast_90_days(self, 
                        start_date: datetime,
                        recurring_income: List[Dict],
                        recurring_expenses: List[Dict],
                        one_time_expenses: List[Dict] = None) -> pd.DataFrame:
        """Forecast balance for next 90 days."""
        
        dates = pd.date_range(start=start_date, periods=90, freq='D')
        balances = []
        current = self.current_balance
        
        for date in dates:
            # Add recurring income
            for income in recurring_income:
                if self._is_payment_due(date, income):
                    current += income.get('amount', 0)
            
            # Subtract recurring expenses
            for expense in recurring_expenses:
                if self._is_payment_due(date, expense):
                    current -= expense.get('amount', 0)
            
            # Apply one-time expenses
            if one_time_expenses:
                for expense in one_time_expenses:
                    if expense.get('date') == date.date():
                        current -= expense.get('amount', 0)
            
            balances.append({
                'date': date,
                'balance': max(0, current),  # Don't go negative
                'below_minimum': current < self.minimum_balance
            })
        
        return pd.DataFrame(balances)
    
    def calculate_safe_payment(self,
                              payment_date: datetime,
                              amount: float,
                              recurring_income: List[Dict],
                              recurring_expenses: List[Dict],
                              future_payments: List[Dict] = None) -> float:
        """Calculate maximum safe amount to pay on given date."""
        
        # Simulate payment
        balance = self.current_balance - amount
        
        # Forecast 90 days with payment
        forecast = self.forecast_90_days(
            payment_date,
            recurring_income,
            recurring_expenses,
            future_payments or []
        )
        
        # Find minimum balance in forecast
        min_balance = forecast['balance'].min()
        
        # Calculate safe amount (never below minimum)
        safe_amount = min(amount, self.current_balance - (self.minimum_balance - min_balance))
        
        return max(0, safe_amount)
    
    def _is_payment_due(self, date: datetime, payment: Dict) -> bool:
        """Check if a payment is due on given date."""
        payment_date = payment.get('date')
        frequency = payment.get('frequency')
        
        if isinstance(payment_date, str):
            payment_date = pd.to_datetime(payment_date)
        
        if frequency == 'monthly':
            return date.day == payment_date.day
        elif frequency == 'weekly':
            return date.weekday() == payment_date.weekday()
        elif frequency == 'daily':
            return True
        else:
            return date == payment_date.date()
    
    def validate_payment_plan(self,
                            payments: List[Tuple[datetime, float]],
                            recurring_income: List[Dict],
                            recurring_expenses: List[Dict]) -> bool:
        """Validate that a payment plan keeps balance above minimum."""
        
        balance = self.current_balance
        
        for payment_date, amount in sorted(payments):
            balance -= amount
            
            if balance < self.minimum_balance:
                return False
        
        return True
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str, rate_date: datetime) -> float:
        """Convert amount between currencies using provided rates."""
        
        if from_currency == to_currency:
            return amount
        
        # Find exchange rate
        rates = self.exchange_rates_df[
            (self.exchange_rates_df['rate_date'] <= rate_date) &
            (self.exchange_rates_df['from_currency'] == from_currency) &
            (self.exchange_rates_df['to_currency'] == to_currency)
        ]
        
        if rates.empty:
            logger.warning(f"No exchange rate found for {from_currency} -> {to_currency}")
            return amount
        
        rate = rates.iloc[-1]['rate']  # Use most recent rate
        return amount * rate

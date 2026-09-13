"""Financial calculation and forecasting engine."""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
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
    
    def calculate_safe_payment(self, amount: float) -> float:
        """Calculate if payment is safe based on current balance and minimum."""
        available = self.current_balance - self.minimum_balance
        return min(amount, max(0, available))
    
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
        
        rate = rates.iloc[-1]['rate']
        return amount * rate

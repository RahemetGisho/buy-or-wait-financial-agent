"""Payment option ranking and selection logic."""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PaymentRanker:
    """Ranks and selects optimal payment options."""
    
    def __init__(self, payment_options_df: pd.DataFrame):
        self.payment_options_df = payment_options_df
    
    def get_eligible_options(self,
                            request_id: str,
                            user_payment_methods: List[str],
                            allows_partial: bool) -> pd.DataFrame:
        """Get payment options eligible for user."""
        
        options = self.payment_options_df[self.payment_options_df['request_id'] == request_id].copy()
        
        if options.empty:
            return pd.DataFrame()
        
        # Filter by user's accepted payment methods
        eligible = []
        for _, opt in options.iterrows():
            method = opt['payment_method']
            if method == 'full_payment' and 'full_payment' in user_payment_methods:
                eligible.append(opt)
            elif method == 'partial_payment' and 'partial_payment' in user_payment_methods and allows_partial:
                eligible.append(opt)
            elif method == 'installments' and 'installments' in user_payment_methods:
                eligible.append(opt)
        
        return pd.DataFrame(eligible) if eligible else pd.DataFrame()
    
    def rank_options(self, eligible_options: pd.DataFrame) -> Optional[Dict]:
        """Rank payment options - prefer full_payment, then installments with fewer payments."""
        
        if eligible_options.empty:
            return None
        
        # Separate by method
        full_payments = eligible_options[eligible_options['payment_method'] == 'full_payment']
        installments = eligible_options[eligible_options['payment_method'] == 'installments']
        partial = eligible_options[eligible_options['payment_method'] == 'partial_payment']
        
        # Prefer full payment
        if not full_payments.empty:
            return full_payments.iloc[0].to_dict()
        
        # Then installments with fewer payments
        if not installments.empty:
            return installments.nsmallest(1, 'number_of_payments').iloc[0].to_dict()
        
        # Finally partial payment
        if not partial.empty:
            return partial.iloc[0].to_dict()
        
        return None
    
    def generate_payment_plan(self, option: Dict) -> str:
        """Generate payment plan string from option."""
        
        first_date = pd.to_datetime(option['first_payment_date'])
        frequency_days = int(option['payment_frequency_days']) if pd.notna(option['payment_frequency_days']) else 0
        num_payments = int(option['number_of_payments'])
        payment_amount = option['payment_amount']
        
        if num_payments == 1:
            return f"{first_date.date()}:{payment_amount}"
        
        payments = []
        for i in range(num_payments):
            if frequency_days > 0:
                payment_date = first_date + pd.Timedelta(days=frequency_days * i)
            else:
                payment_date = first_date
            payments.append(f"{payment_date.date()}:{payment_amount}")
        
        return '|'.join(payments)

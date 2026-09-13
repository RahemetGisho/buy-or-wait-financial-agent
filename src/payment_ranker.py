"""Payment option ranking and selection logic."""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PaymentRanker:
    """Ranks and selects optimal payment options."""
    
    RANKING_CRITERIA = [
        ('complete_by_deadline', True),      # Must complete by deadline
        ('requires_spending_changes', False), # Minimize spending changes
        ('total_cost', False),               # Minimize total cost
        ('start_date', True),                # Start earlier
        ('num_payments', False),             # Fewer payments
        ('payment_option_id', True)          # Lowest ID as tiebreaker
    ]
    
    def __init__(self, payment_options_df: pd.DataFrame):
        self.payment_options_df = payment_options_df
    
    def get_eligible_options(self,
                            request_id: str,
                            user_payment_methods: List[str],
                            allows_partial: bool) -> pd.DataFrame:
        """Get payment options eligible for user."""
        
        options = self.payment_options_df[self.payment_options_df['request_id'] == request_id].copy()
        
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
    
    def rank_options(self,
                    eligible_options: pd.DataFrame,
                    desired_completion_date: datetime,
                    safe_payment_options: List[str]) -> Optional[Dict]:
        """Rank payment options by criteria."""
        
        if eligible_options.empty:
            return None
        
        # Score each option
        scores = []
        for _, opt in eligible_options.iterrows():
            score = self._score_option(
                opt,
                desired_completion_date,
                opt['payment_option_id'] in safe_payment_options
            )
            scores.append((score, opt))
        
        # Sort by score (descending)
        scores.sort(key=lambda x: x[0], reverse=True)
        
        return scores[0][1].to_dict() if scores else None
    
    def _score_option(self, option: pd.Series, deadline: datetime, is_safe: bool) -> Tuple:
        """Score option according to ranking criteria."""
        
        score = []
        
        # 1. Complete by deadline
        last_payment = pd.to_datetime(option['first_payment_date']) + pd.Timedelta(days=option['payment_frequency_days'] * (option['number_of_payments'] - 1))
        score.append(last_payment <= deadline)
        
        # 2. Requires spending changes (assume False for now)
        score.append(False)
        
        # 3. Total cost
        score.append(-option['total_payable_amount'])
        
        # 4. Start date (earlier is better)
        score.append(-pd.to_datetime(option['first_payment_date']).timestamp())
        
        # 5. Number of payments (fewer is better)
        score.append(-option['number_of_payments'])
        
        # 6. Payment option ID
        score.append(option['payment_option_id'])
        
        return tuple(score)
    
    def generate_payment_plan(self, option: Dict) -> str:
        """Generate payment plan string from option."""
        
        first_date = pd.to_datetime(option['first_payment_date'])
        frequency_days = option['payment_frequency_days']
        num_payments = option['number_of_payments']
        payment_amount = option['payment_amount']
        
        payments = []
        for i in range(int(num_payments)):
            payment_date = first_date + pd.Timedelta(days=frequency_days * i)
            payments.append(f"{payment_date.date()}:{payment_amount}")
        
        return '|'.join(payments)

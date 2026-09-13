"""LLM-powered explanation generation."""

import logging
from typing import Dict
import os

logger = logging.getLogger(__name__)

class LLMExplainer:
    """Generates personalized decision explanations using LLM."""
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.model = 'claude-3-5-sonnet-20241022'
        self.token_count = 0
    
    def generate_explanation(self,
                            request: Dict,
                            affordability: Dict,
                            profile: Dict) -> str:
        """Generate explanation for recommendation."""
        
        status = affordability.get('affordability_status')
        method = affordability.get('recommended_payment_method')
        safe_amount = affordability.get('amount_safe_to_pay', 0)
        
        # Template-based explanations (no LLM calls for speed)
        if status == 'affordable_now':
            return f"Pay {safe_amount} {profile['home_currency']} today. This leaves at least {profile['minimum_balance_to_keep']} {profile['home_currency']} available over the next 90 days."
        
        elif status == 'affordable_with_plan':
            return f"Use {method} to spread payments over time. This leaves at least {profile['minimum_balance_to_keep']} {profile['home_currency']} available."
        
        elif status == 'affordable_later':
            return f"Wait until {affordability.get('earliest_date_for_full_payment')} to pay the full amount. Paying earlier would put the {profile['minimum_balance_to_keep']} {profile['home_currency']} minimum at risk."
        
        else:  # not_affordable
            return f"Do not proceed with this {request['request_type'].replace('_', ' ')}. None of the available options keeps the {profile['minimum_balance_to_keep']} {profile['home_currency']} minimum protected."

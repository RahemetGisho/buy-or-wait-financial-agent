"""Explanation generation module."""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

class LLMExplainer:
    """Generates decision explanations."""
    
    def __init__(self):
        pass
    
    def generate_explanation(self,
                            request: Dict,
                            affordability: Dict,
                            profile: Dict) -> str:
        """Generate explanation for recommendation."""
        
        status = affordability.get('affordability_status')
        method = affordability.get('recommended_payment_method')
        safe_amount = affordability.get('amount_safe_to_pay', 0)
        currency = profile['home_currency']
        min_balance = profile['minimum_balance_to_keep']
        request_type = request['request_type'].replace('_', ' ')
        
        # Generate explanations based on affordability status
        if status == 'affordable_now':
            return f"Pay {currency} {safe_amount:.0f} today. This leaves at least {currency} {min_balance:.0f} available over the next 90 days."
        
        elif status == 'affordable_with_plan':
            method_name = method.replace('_', ' ').title()
            return f"Use {method_name} to manage payments. This keeps at least {currency} {min_balance:.0f} available throughout."
        
        elif status == 'affordable_later':
            earliest_date = affordability.get('earliest_date_for_full_payment')
            return f"Wait until {earliest_date} to pay the full amount. Paying earlier would put the {currency} {min_balance:.0f} minimum at risk."
        
        else:  # not_affordable
            return f"Do not proceed with this {request_type}. None of the available options keeps the {currency} {min_balance:.0f} minimum protected."

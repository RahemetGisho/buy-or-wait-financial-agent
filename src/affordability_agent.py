"""Main affordability assessment agent."""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path

from .financial_calculator import FinancialCalculator
from .payment_ranker import PaymentRanker
from .llm_explainer import LLMExplainer

logger = logging.getLogger(__name__)

class AffordabilityAgent:
    """Main agent for evaluating financial affordability."""
    
    def __init__(self,
                 profiles_df: pd.DataFrame,
                 payment_options_df: pd.DataFrame,
                 exchange_rates_df: pd.DataFrame,
                 messages_df: pd.DataFrame,
                 images_df: pd.DataFrame,
                 dataset_path: Path):
        self.profiles_df = profiles_df
        self.payment_options_df = payment_options_df
        self.exchange_rates_df = exchange_rates_df
        self.messages_df = messages_df
        self.images_df = images_df
        self.dataset_path = dataset_path
        self.explainer = LLMExplainer()
    
    def evaluate_request(self, request: Dict) -> Dict:
        """Evaluate a single financial request."""
        
        try:
            # Get user profile
            user_id = request['user_id']
            profile = self.profiles_df[self.profiles_df['user_id'] == user_id].iloc[0].to_dict()
            
            # Parse payment preferences
            payment_methods = self._parse_payment_methods(profile)
            
            # Initialize financial calculator
            calc = FinancialCalculator(profile, self.exchange_rates_df)
            
            # Get payment options
            ranker = PaymentRanker(self.payment_options_df)
            eligible_options = ranker.get_eligible_options(
                request['request_id'],
                payment_methods,
                request['allows_partial_payment']
            )
            
            # Determine affordability
            affordability = self._assess_affordability(
                request,
                profile,
                calc,
                eligible_options,
                ranker
            )
            
            # Generate explanation
            explanation = self.explainer.generate_explanation(
                request,
                affordability,
                profile
            )
            
            return {
                'request_id': request['request_id'],
                'amount_safe_to_pay': affordability.get('amount_safe_to_pay', ''),
                'affordability_status': affordability.get('affordability_status', ''),
                'recommended_payment_method': affordability.get('recommended_payment_method', 'not_recommended'),
                'payment_plan': affordability.get('payment_plan', ''),
                'earliest_date_for_full_payment': affordability.get('earliest_date_for_full_payment', ''),
                'spending_changes_needed': affordability.get('spending_changes_needed', 'none'),
                'decision_explanation': explanation
            }
        
        except Exception as e:
            logger.error(f"Error evaluating request {request.get('request_id')}: {str(e)}")
            raise
    
    def _parse_payment_methods(self, profile: Dict) -> List[str]:
        """Parse user's accepted payment methods."""
        methods_str = profile.get('payment_methods_user_will_consider', '')
        if pd.isna(methods_str) or not methods_str:
            return ['full_payment']
        return [m.strip() for m in str(methods_str).split('|')]
    
    def _assess_affordability(self,
                             request: Dict,
                             profile: Dict,
                             calc: FinancialCalculator,
                             eligible_options: pd.DataFrame,
                             ranker: PaymentRanker) -> Dict:
        """Assess affordability and determine recommendation."""
        
        amount = request['requested_amount']
        completion_date = pd.to_datetime(request['desired_completion_date'])
        request_date = pd.to_datetime(request['request_date'])
        
        # Check if affordable now
        if calc.current_balance >= amount + calc.minimum_balance:
            return {
                'amount_safe_to_pay': amount,
                'affordability_status': 'affordable_now',
                'recommended_payment_method': 'full_payment',
                'payment_plan': f"{request_date.date()}:{amount}",
                'earliest_date_for_full_payment': request_date.date(),
                'spending_changes_needed': 'none'
            }
        
        # Check if affordable with plan
        if not eligible_options.empty:
            best_option = ranker.rank_options(
                eligible_options,
                completion_date,
                []
            )
            if best_option:
                return {
                    'amount_safe_to_pay': 0,
                    'affordability_status': 'affordable_with_plan',
                    'recommended_payment_method': best_option['payment_method'],
                    'payment_plan': ranker.generate_payment_plan(best_option),
                    'earliest_date_for_full_payment': pd.to_datetime(best_option['first_payment_date']).date(),
                    'spending_changes_needed': 'none'
                }
        
        # Check if affordable later
        future_date = request_date + timedelta(days=90)
        if future_date <= completion_date:
            return {
                'amount_safe_to_pay': 0,
                'affordability_status': 'affordable_later',
                'recommended_payment_method': 'wait',
                'payment_plan': f"{completion_date.date()}:{amount}",
                'earliest_date_for_full_payment': completion_date.date(),
                'spending_changes_needed': 'none'
            }
        
        # Not affordable
        return {
            'amount_safe_to_pay': 0,
            'affordability_status': 'not_affordable',
            'recommended_payment_method': 'not_recommended',
            'payment_plan': '',
            'earliest_date_for_full_payment': '',
            'spending_changes_needed': 'none'
        }

#!/usr/bin/env python3
"""
Buy or Wait? - Financial Affordability Agent
Main entry point for processing financial requests and generating recommendations.
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Import core modules
from src.data_loader import DataLoader
from src.affordability_agent import AffordabilityAgent
from src.utils import setup_logging, log_token_usage

def main():
    """Main execution flow."""
    
    # Setup
    setup_logging()
    dataset_path = Path('dataset')
    output_path = Path('output.csv')
    
    print("\n" + "="*80)
    print("BUY OR WAIT? - Financial Affordability Agent")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Dataset path: {dataset_path}")
    print()
    
    # Load all data
    print("[1/4] Loading financial data...")
    loader = DataLoader(dataset_path)
    
    requests_df = loader.load_requests()
    profiles_df = loader.load_financial_profiles()
    payment_options_df = loader.load_payment_options()
    exchange_rates_df = loader.load_exchange_rates()
    messages_df = loader.load_messages()
    images_df = loader.load_images()
    
    print(f"  ✓ Loaded {len(requests_df)} requests")
    print(f"  ✓ Loaded {len(profiles_df)} user profiles")
    print(f"  ✓ Loaded {len(payment_options_df)} payment options")
    print(f"  ✓ Loaded {len(exchange_rates_df)} exchange rates")
    print(f"  ✓ Loaded {len(messages_df)} messages")
    print()
    
    # Initialize agent
    print("[2/4] Initializing affordability agent...")
    agent = AffordabilityAgent(
        profiles_df=profiles_df,
        payment_options_df=payment_options_df,
        exchange_rates_df=exchange_rates_df,
        messages_df=messages_df,
        images_df=images_df,
        dataset_path=dataset_path
    )
    print("  ✓ Agent initialized")
    print()
    
    # Process all requests
    print(f"[3/4] Processing {len(requests_df)} requests...")
    results = []
    
    for idx, (_, request) in enumerate(requests_df.iterrows(), 1):
        try:
            recommendation = agent.evaluate_request(request)
            results.append(recommendation)
            
            if idx % 50 == 0:
                print(f"  ✓ Processed {idx}/{len(requests_df)} requests")
        
        except Exception as e:
            print(f"  ✗ Error processing request {request['request_id']}: {str(e)}")
            results.append({
                'request_id': request['request_id'],
                'amount_safe_to_pay': '',
                'affordability_status': 'error',
                'recommended_payment_method': 'not_recommended',
                'payment_plan': '',
                'earliest_date_for_full_payment': '',
                'spending_changes_needed': 'none',
                'decision_explanation': f'Error: {str(e)}'
            })
    
    print(f"  ✓ Processed all {len(results)} requests")
    print()
    
    # Generate output
    print(f"[4/4] Generating output...")
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)
    print(f"  ✓ Output saved to {output_path}")
    print()
    
    # Summary statistics
    print("Summary Statistics:")
    print(f"  Total requests: {len(results_df)}")
    print(f"  Affordable now: {(results_df['affordability_status'] == 'affordable_now').sum()}")
    print(f"  Affordable with plan: {(results_df['affordability_status'] == 'affordable_with_plan').sum()}")
    print(f"  Affordable later: {(results_df['affordability_status'] == 'affordable_later').sum()}")
    print(f"  Not affordable: {(results_df['affordability_status'] == 'not_affordable').sum()}")
    print()
    
    print("="*80)
    print("✓ Processing complete. Output saved to output.csv")
    print("="*80)

if __name__ == '__main__':
    main()

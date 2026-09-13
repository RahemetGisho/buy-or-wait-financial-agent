"""Utility functions."""

import logging
import sys

token_usage = {'input': 0, 'output': 0, 'total': 0}

def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('execution.log')
        ]
    )

def log_token_usage(input_tokens=0, output_tokens=0):
    """Track token usage."""
    global token_usage
    token_usage['input'] += input_tokens
    token_usage['output'] += output_tokens
    token_usage['total'] = token_usage['input'] + token_usage['output']
    return token_usage

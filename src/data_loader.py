"""Data loading and preprocessing module."""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from PIL import Image
import io

class DataLoader:
    """Loads and validates all input data files."""
    
    def __init__(self, dataset_path: Path):
        self.dataset_path = Path(dataset_path)
        self.media_path = self.dataset_path / 'media' / 'images'
    
    def load_requests(self) -> pd.DataFrame:
        """Load requests.csv"""
        df = pd.read_csv(self.dataset_path / 'requests.csv')
        df['request_date'] = pd.to_datetime(df['request_date'])
        df['desired_completion_date'] = pd.to_datetime(df['desired_completion_date'])
        return df
    
    def load_financial_profiles(self) -> pd.DataFrame:
        """Load financial_profiles.csv"""
        df = pd.read_csv(self.dataset_path / 'financial_profiles.csv')
        return df
    
    def load_payment_options(self) -> pd.DataFrame:
        """Load request_payment_options.csv"""
        df = pd.read_csv(self.dataset_path / 'request_payment_options.csv')
        df['first_payment_date'] = pd.to_datetime(df['first_payment_date'])
        return df
    
    def load_exchange_rates(self) -> pd.DataFrame:
        """Load exchange_rates.csv"""
        df = pd.read_csv(self.dataset_path / 'exchange_rates.csv')
        df['rate_date'] = pd.to_datetime(df['rate_date'])
        return df
    
    def load_messages(self) -> pd.DataFrame:
        """Load messages.csv"""
        df = pd.read_csv(self.dataset_path / 'messages.csv')
        if 'sent_at' in df.columns:
            df['sent_at'] = pd.to_datetime(df['sent_at'])
        return df
    
    def load_images(self) -> pd.DataFrame:
        """Load images.csv"""
        df = pd.read_csv(self.dataset_path / 'images.csv')
        return df
    
    def get_image(self, image_id: str) -> Image.Image:
        """Load an image by ID."""
        image_path = self.media_path / f'{image_id}.png'
        if image_path.exists():
            return Image.open(image_path)
        return None
    
    def extract_amount_from_image(self, image_id: str) -> float:
        """Extract transaction amount from image using OCR-like processing."""
        image = self.get_image(image_id)
        if image is None:
            return None
        # In a real scenario, use pytesseract or Claude's vision API
        # For now, return None to indicate manual review needed
        return None

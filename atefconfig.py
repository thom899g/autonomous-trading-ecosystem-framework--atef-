"""
Configuration management for ATEF.
Handles environment variables, parameter validation, and Firebase initialization.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('atef.log')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TradingConfig:
    """Trading-specific configuration parameters."""
    max_position_size: float = float(os.getenv('MAX_POSITION_SIZE', 0.1))
    max_leverage: float = float(os.getenv('MAX_LEVERAGE', 3.0))
    max_drawdown: float = float(os.getenv('MAX_DRAWDOWN', 0.2))
    initial_capital: float = float(os.getenv('INITIAL_CAPITAL', 10000.0))
    risk_free_rate: float = 0.02
    commission_rate: float = 0.001
    slippage: float = 0.0005
    
    def validate(self) -> None:
        """Validate trading parameters."""
        if self.max_position_size <= 0 or self.max_position_size > 1:
            raise ValueError(f"Invalid max_position_size: {self.max_position_size}")
        if self.max_leverage < 1 or self.max_leverage > 100:
            raise ValueError(f"Invalid max_leverage: {self.max_leverage}")
        if self.max_drawdown <= 0 or self.max_drawdown >= 1:
            raise ValueError(f"Invalid max_drawdown: {self.max_drawdown}")
        if self.initial_capital <= 0:
            raise ValueError(f"Invalid initial_capital: {self.initial_capital}")


@dataclass
class DataConfig:
    """Data configuration parameters."""
    symbols: list[str] = field(default_factory=lambda: ['BTC/USDT', 'ETH/USDT'])
    timeframe: str = '1h'
    lookback_window: int = 1000
    train_test_split: float = 0.8
    min_data_points: int = 100
    
    def validate(self) -> None:
        """Validate data parameters."""
        if self.lookback_window < self.min_data_points:
            raise ValueError(f"lookback_window ({self.lookback_window}) must be >= min_data_points ({self.min_data_points})")
        if self.train_test_split <= 0 or self.train_test_split >= 1:
            raise ValueError(f"Invalid train_test_split: {self.train_test_split}")


class Config:
    """Main configuration class with Firebase integration."""
    
    def __init__(self):
        self.trading = TradingConfig()
        self.data = DataConfig()
        self._firebase_app = None
        self._firestore_client = None
        
        # Validate configurations
        self.trading.validate()
        self.data.validate()
        
        # Initialize Firebase
        self._init_firebase()
        
        logger.info("Configuration initialized successfully")
    
    def _init_firebase(self) -> None:
        """Initialize Firebase Admin SDK with error handling."""
        try:
            creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            
            # Check if credentials file exists
            if not creds_path or not Path(creds_path
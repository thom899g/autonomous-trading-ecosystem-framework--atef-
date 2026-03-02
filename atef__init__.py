"""
Autonomous Trading Ecosystem Framework (ATEF)
Core framework for self-evolving trading strategies and market predictions.
"""

__version__ = "0.1.0"
__author__ = "Evolution Ecosystem"
__license__ = "Proprietary"

from atef.config import Config
from atef.data_integration import DataFetcher
from atef.data_processor import DataProcessor
from atef.model_trainer import ModelTrainer
from atef.strategy_evolver import StrategyEvolver
from atef.execution_engine import ExecutionEngine

__all__ = [
    "Config",
    "DataFetcher",
    "DataProcessor", 
    "ModelTrainer",
    "StrategyEvolver",
    "ExecutionEngine"
]
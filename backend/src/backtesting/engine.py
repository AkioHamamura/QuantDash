# Main backtesting engine using backtrader

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Type
from datetime import datetime
from dataclasses import dataclass
from abc import ABC, abstractmethod
from backtesting.types import Trade
from strategies.base_strategy_class import BaseStrategy # Abstract Base Class import


class BacktestEngine:
    """Main backtesting engine"""

    def __init__(self, strategy: BaseStrategy):
        self.strategy = strategy

    def run(self, data: pd.DataFrame, visualize: bool = True):
        """Run backtest on historical data"""
        # Initialize strategy
        strategy = self.strategy

        # Preprocess data - What should be done here?
        data = strategy.preprocess_data(data)

        # Generate signals - "Does this make a new column in data called 'signals'?"
        data_with_signals = strategy.generate_signals(data)
        
        # Simulate trading - In what format does this return?
        results = strategy.simulate_trading(data_with_signals)

        # Visualize results (True by default)
        viz = strategy.get_json_visualizations(results)

        return results, viz
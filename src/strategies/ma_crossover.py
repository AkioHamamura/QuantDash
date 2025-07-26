# Moving Average Crossover strategy implementation
"""
LEARNING GUIDE: Building a Trading Strategy from Scratch

Key Concepts:
- DataFrame.iterrows() for chronological processing
- Rolling windows for moving averages
- State management for position tracking
- Performance calculation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
import os
from strategies.base_strategy_class import BaseStrategy
from backtesting.metrics import calculate_comprehensive_metrics


class MovingAverageStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy
    
    Strategy Logic:
    - Buy when fast Moving average (average for the last x days) crosses ABOVE slow Moving average (Golden Cross)
    - Sell when fast Moving average crosses BELOW slow Moving average (Death Cross)
    """
    
    # Initialize strategy parameters. For MA strategy: defining fast and slow periods.
    def __init__(self, fast_period: int = 10, slow_period: int = 30, initial_cash: float = 100000):
        """
        Initialize strategy parameters
        
        Args:
            fast_period: Period for fast moving average (e.g., 10 days)
            slow_period: Period for slow moving average (e.g., 30 days)
            initial_cash: Starting capital
        """
        super().__init__(initial_cash=initial_cash)  # Call parent constructor with initial_cash
        self.fast_period = fast_period
        self.slow_period = slow_period
        
        # Store parameters for metrics calculation
        self.parameters = {
            'fast_period': self.fast_period,
            'slow_period': self.slow_period
        }
        
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        STEP 2: Generate buy/sell signals (REQUIRED by BaseStrategy)
        
        Calculate moving averages and crossover signals.
        
        Returns:
            DataFrame with added columns:
            - MA_Fast: Fast moving average
            - MA_Slow: Slow moving average  
            - Buy_Signal: 1 when golden cross occurs, 0 otherwise
            - Sell_Signal: 1 when death cross occurs, 0 otherwise
        """
        df = data.copy() # Create a copy to avoid modifying original data

        # Calculate moving averages at close prices
        df['MA_Fast'] = df['Close'].rolling(window=self.fast_period).mean() # Create Fast MA column in DataFrame
        df['MA_Slow'] = df['Close'].rolling(window=self.slow_period).mean() # Create Slow MA column in DataFrame
        
        # Calculate crossover signals
        # 1 when fast MA > slow MA, 0 otherwise
        df['Fast_Above_Slow'] = (df['MA_Fast'] > df['MA_Slow']).astype(int) # binary column for fast above slow
        
        # Detect crossovers: difference between current and previous signal
        df['Signal_Change'] = df['Fast_Above_Slow'].diff() # 1 when fast crosses above slow, -1 when fast crosses below slow
        
        # Generate explicit buy/sell signals
        df['Buy_Signal'] = 0   # Initialize
        df['Sell_Signal'] = 0  # Initialize
        
        # Signal_Change = 1 means golden cross (fast MA crossed above slow MA)
        # locates where Signal_Change is 1 and sets Buy_Signal to 1
        df.loc[df['Signal_Change'] == 1, 'Buy_Signal'] = 1
        
        # Signal_Change = -1 means death cross (fast MA crossed below slow MA)  
        # locates where Signal_Change is -1 and sets Sell_Signal to 1
        df.loc[df['Signal_Change'] == -1, 'Sell_Signal'] = 1
        
        print(df)  # Print rows for debugging <---------------
        return df


# Test function to verify the strategy works
def test_ma_strategy():
    """Test the Moving Average strategy with sample data"""
    from data.data_fetcher import fetch_stock_data
    from backtesting.engine import BacktestEngine
    
    print("=== Testing Moving Average Crossover Strategy ===")
    
    # Fetch test data
    data = fetch_stock_data("NVDA", period="1y")
    if data is None or data.empty:
        print("Failed to fetch data")
        return
    
    # Create strategy
    strategy = MovingAverageStrategy(fast_period=10, slow_period=30)
    
    # Create engine and run backtest
    backtesting_engine = BacktestEngine(strategy)
    results = backtesting_engine.run(data)

    # Display results
    print("\n" + "="*50)
    print("BACKTEST RESULTS")
    print("="*50)
    print(f"Strategy: {results['strategy']}")
    print(f"Parameters: Fast MA = {results['parameters']['fast_period']}, Slow MA = {results['parameters']['slow_period']}")
    print(f"Initial Cash: ${results['initial_cash']:,.2f}")
    print(f"Final Value: ${results['final_value']:,.2f}")
    print(f"Total Return: {results['total_return_pct']:.2f}%")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Win Rate: {results['win_rate_pct']:.1f}%")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.3f}")
    print(f"Sortino Ratio: {results['sortino_ratio']:.3f}")
    print(f"Volatility: {results['volatility_pct']:.2f}%")
    print(f"Max Drawdown: {results['max_drawdown_pct']:.2f}%")
    print(f"Max Drawdown Duration: {results['max_drawdown_duration']} days")





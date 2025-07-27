
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Type
from abc import ABC, abstractmethod # Abstract Base Class import
from src.backtesting.types import Trade


class BaseStrategy(ABC):
    """
    Base class for trading strategies
    
    The BaseStrategy class defines the fundamental structure for any trading strategy.
    It includes methods for preprocessing data, generating buy/sell signals (has to be overridden), and simulating trading.
    
    Subclasses must implement the generate_signals method and can override simulate_trading if needed.
    All attributes and methods here are guaranteed to be available in all trading strategies.
    """
    
    def __init__(self, initial_cash: float = 100000):
        """Initialize the strategy with portfolio state"""
        self.initial_cash = initial_cash
        
        # Portfolio state (will be reset for each backtest)
        self.cash = initial_cash
        self.shares = 0
        self.position = 0  # 0 = no position, 1 = long
        
        # Performance tracking
        self.trades: List[Trade] = []
        self.portfolio_values: List[float] = []

    def reset_portfolio(self):
        """Reset portfolio state for fresh backtest"""
        self.cash = self.initial_cash
        self.shares = 0
        self.position = 0
        self.trades = []
        self.portfolio_values = []

    def _safe_extract_value(self, value):
        """Safely extract scalar value from potentially multi-index Series"""
        if hasattr(value, 'item'):
            return value.item()
        return value

    def _execute_buy(self, date, current_price, verbose: bool = True):
        """Execute a buy order if not already in position"""
        if self.position == 0:  # Only buy if no position
            self.shares = int(self.cash / current_price)
            cost = self.shares * current_price
            self.cash = self.cash - cost
            self.position = 1
            
            # Record trade entry
            from src.utils.helpers import convert_date_to_datetime
            date_obj = convert_date_to_datetime(date)
            trade = Trade(
                entry_date=date_obj,
                entry_price=current_price,
                shares=self.shares
            )
            self.trades.append(trade)

            if verbose:
                print(f"{date_obj.strftime('%Y-%m-%d')}: BUY {self.shares} shares at ${current_price:.2f} for ${cost:.2f}")
            return True
        return False

    def _execute_sell(self, date, current_price, verbose: bool = True):
        """Execute a sell order if in position"""
        if self.position == 1:  # Only sell if in position
            self.cash = self.shares * current_price
            
            # Complete the last trade record
            if self.trades:
                last_trade = self.trades[-1]
                from src.utils.helpers import convert_date_to_datetime
                date_obj = convert_date_to_datetime(date)
                last_trade.exit_date = date_obj
                last_trade.exit_price = current_price
                last_trade.profit_loss = (current_price - last_trade.entry_price) * last_trade.shares
            
            self.shares = 0
            self.position = 0
            
            if verbose:
                date_obj = convert_date_to_datetime(date)
                print(f"{date_obj.strftime('%Y-%m-%d')}: SELL at ${current_price:.2f} for ${self.cash:.2f}")
            return True
        return False

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        STEP 1: Preprocess data

        Sorts by date and ensures data integrity.
        """
        # Make a copy to avoid modifying original data
        df = data.copy()
        
        # Ensure we have required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Sort by date to ensure chronological order
        df = df.sort_index()
        
        return df


    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on strategy logic"""
        raise NotImplementedError("Subclasses must implement generate_signals method")


    @abstractmethod
    def visualize_results(self, results: Dict):
        """
        Visualizes the results of a backtest using Plotly for interactive charts.
        
        Should be overridden by subclasses to provide strategy-specific visualizations.
        """
        raise NotImplementedError("Subclasses must implement visualize_results method")


    def simulate_trading(self, data: pd.DataFrame, verbose: bool = True) -> Dict:
        """
        Default trading simulation logic
        
        Can be overridden by subclasses for custom trading logic.
        Expects data to have 'Buy_Signal' and 'Sell_Signal' columns.
        """
        # Reset portfolio state for fresh backtest
        self.reset_portfolio()
        
        # Process each day chronologically
        for date, row in data.iterrows():
            # Handle scalar access for potentially multi-index columns
            current_price = self._safe_extract_value(row['Close'])
            
            # Get signal values safely
            buy_signal = self._safe_extract_value(row['Buy_Signal'])
            sell_signal = self._safe_extract_value(row['Sell_Signal'])
            
            # EXECUTE BUY SIGNAL
            if buy_signal == 1:
                self._execute_buy(date, current_price, verbose)
                
            # EXECUTE SELL SIGNAL  
            elif sell_signal == 1:
                self._execute_sell(date, current_price, verbose)
            
            # Calculate current portfolio value
            portfolio_value = self.cash + (self.shares * current_price)
            self.portfolio_values.append(portfolio_value)
        
        # Add portfolio values to the data for visualization
        data = data.copy()
        data['Portfolio_Value'] = self.portfolio_values
        
        # Calculate drawdown for visualization
        peak = data['Portfolio_Value'].expanding().max()
        data['Drawdown'] = data['Portfolio_Value'] - peak
        data['Drawdown_Pct'] = (data['Drawdown'] / peak) * 100
        
        # Calculate and return performance metrics
        metrics = self.calculate_performance_metrics(data)
        
        # Add the processed data to metrics for visualization
        metrics['data'] = data
        
        return metrics

    def calculate_performance_metrics(self, data: pd.DataFrame) -> Dict:
        """
        Calculate performance metrics using the metrics module
        
        Should be overridden by subclasses to provide strategy-specific metrics.
        """
        from src.backtesting.metrics import calculate_comprehensive_metrics
        
        # Get completed trades
        completed_trades = [t for t in self.trades if t.exit_date is not None]
        
        # Use the comprehensive metrics calculation from the metrics module
        return calculate_comprehensive_metrics(
            strategy_name=self.__class__.__name__,
            parameters=getattr(self, 'parameters', {}),
            initial_cash=self.initial_cash,
            portfolio_values=self.portfolio_values,
            completed_trades=completed_trades,
            data_index=data.index,
            risk_free_rate=0.0  # Default risk-free rate
        )
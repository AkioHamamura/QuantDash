# Creating New Trading Strategies

This guide explains how to create new trading strategies using the QuantDash framework's modular `BaseStrategy` class.

## 🏗️ Architecture Overview

The QuantDash system uses an abstract base class pattern that allows you to create new strategies by implementing just the signal generation logic. All the backtesting, portfolio management, and metrics calculation are handled automatically.

## 📋 Requirements for New Strategies

To create a new strategy, you need to:

1. **Inherit from BaseStrategy**: Import and extend the abstract base class
2. **Implement generate_signals()**: Define your buy/sell signal logic
3. **Set parameters dict**: Store strategy-specific parameters
4. **Follow naming conventions**: Use clear, descriptive class and file names

## 🎯 Step-by-Step Guide

### Step 1: Create Strategy File

Create a new Python file in `src/strategies/` following the naming pattern:
```
src/strategies/your_strategy_name.py
```

### Step 2: Basic Template

```python
import pandas as pd
import numpy as np
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.strategies.base_strategy_class import BaseStrategy


class YourStrategyName(BaseStrategy):
    """
    Description of your trading strategy
    
    Parameters:
        param1: Description of parameter 1
        param2: Description of parameter 2
    """
    
    def __init__(self, param1=default_value, param2=default_value, initial_cash=100000):
        super().__init__(initial_cash)
        
        # Store strategy parameters
        self.parameters = {
            'param1': param1,
            'param2': param2
        }
        
        # Store individual parameters for easy access
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals based on your strategy logic
        
        Args:
            data: DataFrame with OHLCV data (Open, High, Low, Close, Volume)
            
        Returns:
            DataFrame with original data plus 'Buy_Signal' and 'Sell_Signal' columns
        """
        # Make a copy to avoid modifying original data
        df = data.copy()
        
        # Initialize signal columns
        df['Buy_Signal'] = False
        df['Sell_Signal'] = False
        
        # YOUR STRATEGY LOGIC GOES HERE

        # Generate buy signals
        df['Buy_Signal'] = ...
        
        # Generate sell signals
        df['Sell_Signal'] = ...
        
        return df


# Example usage and testing
if __name__ == "__main__":
    from src.data.data_fetcher import fetch_stock_data
    from src.backtesting.metrics import calculate_comprehensive_metrics
    
    # Test the strategy
    strategy = YourStrategyName(param1=20, param2=50)
    
    # Fetch test data
    data = fetch_stock_data('AAPL', period='2y')
    
    # Run backtest
    processed_data = strategy.preprocess_data(data)
    signal_data = strategy.generate_signals(processed_data)
    results = strategy.simulate_trading(signal_data, verbose=True)
    
    # Calculate metrics
    metrics = calculate_comprehensive_metrics(
        strategy_name="Your Strategy Name",
        parameters=strategy.parameters,
        initial_cash=strategy.initial_cash,
        portfolio_values=strategy.portfolio_values,
        completed_trades=[t for t in strategy.trades if t.exit_date is not None],
        data_index=signal_data.index
    )
    
    print(f"\\n=== {metrics['strategy']} Performance ===")
    print(f"Parameters: {metrics['parameters']}")
    print(f"Total Return: {metrics['total_return_pct']:.2f}%")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
    print(f"Win Rate: {metrics['win_rate_pct']:.2f}%")
```

## 🎯 Strategy Examples

### Example 1: RSI Pullback Strategy

```python
class RSIPullbackStrategy(BaseStrategy):
    """
    Buy when RSI is oversold (< 30) and sell when overbought (> 70)
    """
    
    def __init__(self, rsi_period=14, oversold=30, overbought=70, initial_cash=100000):
        super().__init__(initial_cash)
        self.parameters = {
            'rsi_period': rsi_period,
            'oversold': oversold,
            'overbought': overbought
        }
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_rsi(self, prices, period):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Calculate RSI
        df['RSI'] = self.calculate_rsi(df['Close'], self.rsi_period)
        
        # Initialize signals
        df['Buy_Signal'] = False
        df['Sell_Signal'] = False
        
        # Generate signals
        df['Buy_Signal'] = df['RSI'] < self.oversold
        df['Sell_Signal'] = df['RSI'] > self.overbought
        
        return df
```

### Example 2: Bollinger Bands Strategy

```python
class BollingerBandsStrategy(BaseStrategy):
    """
    Buy when price touches lower band, sell when price touches upper band
    """
    
    def __init__(self, period=20, std_dev=2, initial_cash=100000):
        super().__init__(initial_cash)
        self.parameters = {
            'period': period,
            'std_dev': std_dev
        }
        self.period = period
        self.std_dev = std_dev
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Calculate Bollinger Bands
        df['SMA'] = df['Close'].rolling(window=self.period).mean()
        df['STD'] = df['Close'].rolling(window=self.period).std()
        df['Upper_Band'] = df['SMA'] + (df['STD'] * self.std_dev)
        df['Lower_Band'] = df['SMA'] - (df['STD'] * self.std_dev)
        
        # Initialize signals
        df['Buy_Signal'] = False
        df['Sell_Signal'] = False
        
        # Generate signals
        df['Buy_Signal'] = df['Close'] <= df['Lower_Band']
        df['Sell_Signal'] = df['Close'] >= df['Upper_Band']
        
        return df
```

## 🔧 Advanced Customization

### Custom Trading Logic

If you need custom trading logic (beyond simple buy/sell signals), you can override the `simulate_trading` method:

```python
def simulate_trading(self, data: pd.DataFrame, verbose: bool = True) -> Dict:
    """Custom trading logic with position sizing, stop losses, etc."""
    self.reset_portfolio()
    
    for date, row in data.iterrows():
        current_price = self._safe_extract_value(row['Close'])
        
        # Your custom trading logic here
        # Example: Position sizing based on volatility
        volatility = data['Close'].rolling(20).std().loc[date]
        position_size = min(0.02, 0.1 / volatility)  # Risk-adjusted sizing
        
        # Implement your custom buy/sell logic
        
    return {
        'strategy': self.__class__.__name__,
        'parameters': self.parameters,
        'final_value': self.cash + (self.shares * current_price),
        'trades': self.trades
    }
```

## 📊 Testing Your Strategy

### Quick Test Template

```python
def test_strategy():
    """Quick test function for your strategy"""
    # Initialize strategy
    strategy = YourStrategyName(param1=value1, param2=value2)
    
    # Get test data
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    for ticker in tickers:
        print(f"\\n=== Testing {ticker} ===")
        data = fetch_stock_data(ticker, period='1y')
        
        # Run backtest
        processed_data = strategy.preprocess_data(data)
        signal_data = strategy.generate_signals(processed_data)
        results = strategy.simulate_trading(signal_data, verbose=False)
        
        # Calculate metrics
        metrics = calculate_comprehensive_metrics(
            strategy_name=strategy.__class__.__name__,
            parameters=strategy.parameters,
            initial_cash=strategy.initial_cash,
            portfolio_values=strategy.portfolio_values,
            completed_trades=[t for t in strategy.trades if t.exit_date is not None],
            data_index=signal_data.index
        )
        
        print(f"Return: {metrics['total_return_pct']:.2f}% | Sharpe: {metrics['sharpe_ratio']:.2f} | Drawdown: {metrics['max_drawdown_pct']:.2f}%")

if __name__ == "__main__":
    test_strategy()
```

## ✅ Best Practices

1. **Parameter Documentation**: Clearly document what each parameter does
2. **Error Handling**: Add checks for invalid parameters or data issues
3. **Signal Logic**: Ensure buy/sell signals are mutually exclusive
4. **Data Validation**: Check for required columns and data quality
5. **Testing**: Test with multiple tickers and time periods
6. **Performance**: Consider computational efficiency for large datasets

## 🚀 Integration with Dashboard

Once your strategy is created, it will automatically work with the QuantDash dashboard system. The dashboard can:

- Load your strategy dynamically
- Display parameter controls
- Show performance metrics
- Plot equity curves and signals
- Compare against other strategies

## 📁 File Organization

```
src/strategies/
├── base_strategy_class.py    # Abstract base class
├── ma_crossover.py          # Moving Average Crossover example
├── rsi_pullback.py          # Your RSI strategy
├── bollinger_bands.py       # Your Bollinger Bands strategy
└── your_custom_strategy.py  # Your new strategy
```

## 🔍 Debugging Tips

1. **Print Intermediate Values**: Use `print()` statements to check calculations
2. **Check Signal Counts**: Verify reasonable number of buy/sell signals
3. **Validate Data**: Ensure no NaN values in critical calculations
4. **Test Edge Cases**: Try different market conditions and time periods
5. **Compare Results**: Cross-reference with other backtesting tools

This framework makes it easy to implement, test, and deploy new trading strategies while maintaining consistent performance measurement and visualization capabilities.

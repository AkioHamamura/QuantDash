# QuantDash Performance Metrics Documentation

This document explains all the performance metrics calculated by the `calculate_comprehensive_metrics` function in `src/backtesting/metrics.py`.

## 📊 Overview

The metrics system provides a comprehensive evaluation of trading strategy performance, covering profitability, risk management, and statistical measures. All metrics are calculated from the portfolio's historical performance and completed trades.

## 📈 Basic Performance Metrics

### Initial Cash
- **Description**: Starting capital for the backtest
- **Unit**: Currency (USD)
- **Usage**: Baseline for calculating returns and profit/loss

### Final Value
- **Description**: Portfolio value at the end of the backtest period
- **Unit**: Currency (USD)
- **Formula**: Cash + (Shares × Final Price)

### Total Return (%)
- **Description**: Overall percentage gain/loss from initial capital
- **Unit**: Percentage
- **Formula**: `((Final Value - Initial Cash) / Initial Cash) × 100`
- **Interpretation**: 
  - Positive values indicate profit
  - Negative values indicate loss

### Total Profit
- **Description**: Absolute dollar profit/loss from all completed trades
- **Unit**: Currency (USD)
- **Formula**: Sum of all trade profit_loss values

## 📊 Trade Analysis Metrics

### Total Trades
- **Description**: Number of completed round-trip trades (buy + sell)
- **Unit**: Count
- **Note**: Open positions are not included in this count

### Winning Trades
- **Description**: Number of profitable trades
- **Unit**: Count
- **Criteria**: Trades with profit_loss > 0

### Win Rate (%)
- **Description**: Percentage of trades that were profitable
- **Unit**: Percentage
- **Formula**: `(Winning Trades / Total Trades) × 100`
- **Interpretation**:
  - 50%+ indicates more winning than losing trades
  - Higher win rates suggest consistent strategy performance

## ⚖️ Risk-Adjusted Performance Metrics

### Sharpe Ratio
- **Description**: Risk-adjusted return measure
- **Unit**: Ratio (dimensionless)
- **Formula**: `(Portfolio Return - Risk-Free Rate) / Portfolio Volatility`
- **Annualized**: Yes (assumes 252 trading days per year)
- **Interpretation**:
  - > 1.0: Good risk-adjusted performance
  - > 2.0: Excellent risk-adjusted performance
  - < 0: Returns below risk-free rate

### Sortino Ratio
- **Description**: Downside risk-adjusted return measure
- **Unit**: Ratio (dimensionless)
- **Formula**: `(Portfolio Return - Risk-Free Rate) / Downside Deviation`
- **Key Difference**: Only considers negative volatility (downside risk)
- **Interpretation**:
  - Higher values indicate better downside risk management
  - More relevant than Sharpe for strategies with asymmetric returns

## 📉 Drawdown Metrics

### Maximum Drawdown (%)
- **Description**: Largest peak-to-trough decline in portfolio value
- **Unit**: Percentage
- **Formula**: `Max((Peak Value - Trough Value) / Peak Value) × 100`
- **Interpretation**:
  - Lower values indicate better capital preservation
  - Critical for understanding worst-case scenarios

### Maximum Drawdown Duration
- **Description**: Longest time period (in days) spent in drawdown
- **Unit**: Days
- **Interpretation**:
  - Shorter durations indicate faster recovery from losses
  - Important for psychological trading factors

## 📊 Volatility Metrics

### Volatility (%)
- **Description**: Annualized standard deviation of daily returns
- **Unit**: Percentage
- **Formula**: `Daily Return Std Dev × √252 × 100`
- **Interpretation**:
  - Lower values indicate more stable returns
  - Higher values suggest more unpredictable performance

## 🔍 Strategy-Specific Information

### Strategy Name
- **Description**: Identifier for the trading strategy used
- **Examples**: "Moving Average Crossover", "RSI Pullback"

### Parameters
- **Description**: Dictionary of strategy-specific parameters
- **Format**: Key-value pairs
- **Examples**: 
  - `{"short_window": 20, "long_window": 50}` for MA Crossover
  - `{"rsi_period": 14, "oversold": 30}` for RSI strategy

## 📈 Time Series Data (For Plotting)

The metrics function also returns complete time series data for visualization:

### Portfolio Values
- **Description**: List of portfolio values for each trading day
- **Usage**: Plotting equity curves and portfolio growth

### Trades
- **Description**: List of Trade objects with entry/exit details
- **Fields**: entry_date, exit_date, shares, entry_price, exit_price, profit_loss
- **Usage**: Trade-by-trade analysis and visualization

## 🎯 Key Performance Indicators (KPIs)

For dashboard display, focus on these primary metrics:

1. **Total Return (%)** - Overall profitability
2. **Sharpe Ratio** - Risk-adjusted performance
3. **Maximum Drawdown (%)** - Worst-case loss
4. **Win Rate (%)** - Strategy consistency
5. **Volatility (%)** - Return stability

## 📊 Benchmark Comparison

When evaluating strategies, compare against:
- **Buy & Hold**: Simple index investment
- **Risk-Free Rate**: Treasury bills/bonds
- **Market Indices**: S&P 500, sector ETFs

## ⚠️ Important Notes

1. **Risk-Free Rate**: Default is 0%, but can be adjusted for current market conditions
2. **Annualization**: Assumes 252 trading days per year
3. **Open Positions**: Only completed trades are included in trade analysis
4. **Data Quality**: Metrics accuracy depends on clean, chronological price data
5. **Survivorship Bias**: Historical backtests may not reflect future performance

## 🔧 Technical Implementation

- **Module**: `src/backtesting/metrics.py`
- **Main Function**: `calculate_comprehensive_metrics()`
- **Dependencies**: pandas, numpy, datetime
- **Return Type**: Dictionary with all metrics and time series data

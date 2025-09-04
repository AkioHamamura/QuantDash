# Performance metrics calculation (Sharpe, Sortino, etc.)
"""
Performance Metrics Module

This module contains functions to calculate various trading performance metrics
that can be used across different strategies and backtesting engines.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from .types import Trade


def calculate_basic_metrics(
    initial_cash: float,
    portfolio_values: List[float],
    completed_trades: List[Trade]
) -> Dict:
    """
    Calculate basic performance metrics
    
    Args:
        initial_cash: Starting capital
        portfolio_values: List of portfolio values over time
        completed_trades: List of completed Trade objects
        
    Returns:
        Dict with basic metrics
    """
    final_value = portfolio_values[-1] if portfolio_values else initial_cash
    total_return = (final_value - initial_cash) / initial_cash
    
    # Trade analysis
    total_profit = sum(t.profit_loss for t in completed_trades)
    winning_trades = len([t for t in completed_trades if t.profit_loss > 0])
    total_trades = len(completed_trades)
    win_rate = (winning_trades / total_trades) if total_trades > 0 else 0
    
    return {
        'initial_cash': initial_cash,
        'final_value': final_value,
        'total_return_pct': total_return * 100,
        'total_profit': total_profit,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'win_rate_pct': win_rate * 100,
    }


def calculate_sharpe_ratio(
    portfolio_values: List[float], 
    data_index: pd.Index,
    risk_free_rate: float = 0.0
) -> float:
    """
    Calculate Sharpe ratio (risk-adjusted return)
    
    Args:
        portfolio_values: List of portfolio values over time
        data_index: DatetimeIndex for the portfolio values
        risk_free_rate: Annual risk-free rate (default: 0%)
        
    Returns:
        Annualized Sharpe ratio
    """
    if len(portfolio_values) < 2:
        return 0.0
        
    portfolio_series = pd.Series(portfolio_values, index=data_index[-len(portfolio_values):])
    daily_returns = portfolio_series.pct_change().dropna()
    
    if len(daily_returns) < 2 or daily_returns.std() == 0:
        return 0.0
    
    # Calculate excess return over risk-free rate
    daily_rf_rate = risk_free_rate / 252  # Convert annual to daily
    excess_returns = daily_returns - daily_rf_rate
    
    # Annualized Sharpe ratio
    sharpe_ratio = excess_returns.mean() / daily_returns.std() * np.sqrt(252)
    
    return sharpe_ratio


def calculate_sortino_ratio(
    portfolio_values: List[float],
    data_index: pd.Index,
    risk_free_rate: float = 0.0
) -> float:
    """
    Calculate Sortino ratio (downside deviation adjusted return)
    
    Args:
        portfolio_values: List of portfolio values over time
        data_index: DatetimeIndex for the portfolio values
        risk_free_rate: Annual risk-free rate (default: 0%)
        
    Returns:
        Annualized Sortino ratio
    """
    if len(portfolio_values) < 2:
        return 0.0
        
    portfolio_series = pd.Series(portfolio_values, index=data_index[-len(portfolio_values):])
    daily_returns = portfolio_series.pct_change().dropna()
    
    if len(daily_returns) < 2:
        return 0.0
    
    # Calculate downside deviation (only negative returns)
    daily_rf_rate = risk_free_rate / 252
    excess_returns = daily_returns - daily_rf_rate
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0:
        return float('inf')  # No downside, infinite Sortino ratio
    
    downside_deviation = downside_returns.std()
    if downside_deviation == 0:
        return 0.0
    
    # Annualized Sortino ratio
    sortino_ratio = excess_returns.mean() / downside_deviation * np.sqrt(252)
    
    return sortino_ratio


def calculate_max_drawdown(portfolio_values: List[float]) -> Dict:
    """
    Calculate maximum drawdown and drawdown duration
    
    Args:
        portfolio_values: List of portfolio values over time
        
    Returns:
        Dict with max drawdown percentage and duration
    """
    if len(portfolio_values) < 2:
        return {'max_drawdown_pct': 0.0, 'max_drawdown_duration': 0}
    
    portfolio_series = pd.Series(portfolio_values)
    peak = portfolio_series.expanding().max()
    drawdown = (portfolio_series - peak) / peak
    max_drawdown = drawdown.min()
    
    # Calculate maximum drawdown duration
    drawdown_periods = []
    current_drawdown_start = None
    
    for i, dd in enumerate(drawdown):
        if dd < 0 and current_drawdown_start is None:
            current_drawdown_start = i
        elif dd == 0 and current_drawdown_start is not None:
            drawdown_periods.append(i - current_drawdown_start)
            current_drawdown_start = None
    
    # Handle case where drawdown continues to end
    if current_drawdown_start is not None:
        drawdown_periods.append(len(drawdown) - current_drawdown_start)
    
    max_drawdown_duration = max(drawdown_periods) if drawdown_periods else 0
    
    return {
        'max_drawdown_pct': max_drawdown * 100,
        'max_drawdown_duration': max_drawdown_duration
    }


def calculate_volatility(
    portfolio_values: List[float],
    data_index: pd.Index
) -> float:
    """
    Calculate annualized volatility (standard deviation of returns)
    
    Args:
        portfolio_values: List of portfolio values over time
        data_index: DatetimeIndex for the portfolio values
        
    Returns:
        Annualized volatility percentage
    """
    if len(portfolio_values) < 2:
        return 0.0
        
    portfolio_series = pd.Series(portfolio_values, index=data_index[-len(portfolio_values):])
    daily_returns = portfolio_series.pct_change().dropna()
    
    if len(daily_returns) < 2:
        return 0.0
    
    # Annualized volatility
    volatility = daily_returns.std() * np.sqrt(252) * 100
    
    return volatility


def calculate_comprehensive_metrics(
    strategy_name: str,
    parameters: Dict,
    initial_cash: float,
    portfolio_values: List[float],
    completed_trades: List[Trade],
    data_index: pd.Index,
    risk_free_rate: float = 0.0
) -> Dict:
    """
    Calculate comprehensive performance metrics for a trading strategy
    
    Args:
        strategy_name: Name of the strategy
        parameters: Strategy parameters dict
        initial_cash: Starting capital
        portfolio_values: List of portfolio values over time
        completed_trades: List of completed Trade objects
        data_index: DatetimeIndex for the portfolio values
        risk_free_rate: Annual risk-free rate (default: 0%)
        
    Returns:
        Dict with all performance metrics
    """
    # Basic metrics
    basic_metrics = calculate_basic_metrics(initial_cash, portfolio_values, completed_trades)
    
    # Risk-adjusted metrics
    sharpe_ratio = calculate_sharpe_ratio(portfolio_values, data_index, risk_free_rate)
    sortino_ratio = calculate_sortino_ratio(portfolio_values, data_index, risk_free_rate)
    
    # Drawdown metrics
    drawdown_metrics = calculate_max_drawdown(portfolio_values)
    
    # Volatility
    volatility = calculate_volatility(portfolio_values, data_index)
    
    # Combine all metrics
    return {
        'strategy': strategy_name,
        'parameters': parameters,
        **basic_metrics,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        **drawdown_metrics,
        'volatility_pct': volatility,
        'portfolio_values': portfolio_values,
        'trades': completed_trades
    }
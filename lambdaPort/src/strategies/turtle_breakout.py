# Turtle Channel Breakout strategy implementation
"""
Turtle Trading Strategy

Key Concepts:
- Channel breakouts: Price breaking above/below recent highs/lows
- Position sizing: Risk-based position management
- Trend following: Riding momentum after breakouts
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Tuple, Optional
import plotly.graph_objects as go
import plotly.io as pio
from dataclasses import dataclass
from datetime import datetime
import sys
import os
from .base_strategy_class import BaseStrategy
from ..backtesting.metrics import calculate_comprehensive_metrics


class TurtleBreakout(BaseStrategy):
    """
    Turtle Trading Breakout Strategy
    
    Strategy Logic:
    - Buy when price breaks above N-day high (entry breakout)
    - Sell when price breaks below M-day low (exit breakout)
    - Use ATR for position sizing and stop losses
    """
    
    def __init__(self, entry_period: int = 20, exit_period: int = 10, 
                 atr_period: int = 20, risk_percent: float = 0.02, initial_cash: float = 100000):
        """
        Initialize strategy parameters
        
        Args:
            entry_period: Period for entry breakout calculation
            exit_period: Period for exit breakout calculation
            atr_period: Period for ATR calculation
            risk_percent: Risk percentage per trade
            initial_cash: Starting capital
        """
        super().__init__(name="Turtle Breakout", initial_cash=initial_cash)
        self.entry_period = entry_period
        self.exit_period = exit_period
        self.atr_period = atr_period
        self.risk_percent = risk_percent
        
        # Store parameters for metrics calculation
        self.parameters = {
            'entry_period': self.entry_period,
            'exit_period': self.exit_period,
            'atr_period': self.atr_period,
            'risk_percent': self.risk_percent,
            'initial_cash': self.initial_cash
        }
    
    def calculate_atr(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate Average True Range (ATR)
        
        Args:
            data: DataFrame with OHLC data
            
        Returns:
            Series with ATR values
        """
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift(1))
        low_close = abs(data['Low'] - data['Close'].shift(1))
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=self.atr_period).mean()
        
        return atr
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on turtle breakout strategy
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional columns for signals and indicators
        """
        df = data.copy()
        
        # Calculate breakout levels
        df['entry_high'] = df['High'].rolling(window=self.entry_period).max()
        df['entry_low'] = df['Low'].rolling(window=self.entry_period).min()
        df['exit_high'] = df['High'].rolling(window=self.exit_period).max()
        df['exit_low'] = df['Low'].rolling(window=self.exit_period).min()
        
        # Calculate ATR for position sizing
        df['atr'] = self.calculate_atr(df)
        
        # Initialize signal columns
        df['signal'] = 0
        df['position'] = 0
        df['stop_loss'] = np.nan
        df['position_size'] = 0
        
        # Generate signals
        current_position = 0
        entry_price = None
        stop_loss = None
        position_size = 0
        
        for i in range(max(self.entry_period, self.exit_period, self.atr_period), len(df)):
            current_high = df['High'].iloc[i]
            current_low = df['Low'].iloc[i]
            current_close = df['Close'].iloc[i]
            entry_high = df['entry_high'].iloc[i-1]  # Previous day's level
            entry_low = df['entry_low'].iloc[i-1]
            exit_high = df['exit_high'].iloc[i-1]
            exit_low = df['exit_low'].iloc[i-1]
            current_atr = df['atr'].iloc[i]
            
            # Skip if we don't have enough data
            if pd.isna(entry_high) or pd.isna(current_atr):
                df.loc[df.index[i], 'position'] = current_position
                continue
            
            if current_position == 0:  # No position
                # Long breakout signal
                if current_high > entry_high:
                    # Calculate position size based on risk
                    risk_amount = self.initial_cash * self.risk_percent
                    position_size = risk_amount / (2 * current_atr)  # 2N stop
                    
                    df.loc[df.index[i], 'signal'] = 1  # Buy signal
                    current_position = 1
                    entry_price = current_close
                    stop_loss = entry_price - (2 * current_atr)
                
                # Short breakout signal
                elif current_low < entry_low:
                    # Calculate position size based on risk
                    risk_amount = self.initial_cash * self.risk_percent
                    position_size = risk_amount / (2 * current_atr)  # 2N stop
                    
                    df.loc[df.index[i], 'signal'] = -1  # Sell signal
                    current_position = -1
                    entry_price = current_close
                    stop_loss = entry_price + (2 * current_atr)
            
            elif current_position == 1:  # Long position
                # Exit signals for long position
                if (current_low < exit_low or  # Exit breakout
                    current_low <= stop_loss):  # Stop loss
                    df.loc[df.index[i], 'signal'] = -1  # Sell signal
                    current_position = 0
                    entry_price = None
                    stop_loss = None
                    position_size = 0
            
            elif current_position == -1:  # Short position
                # Exit signals for short position
                if (current_high > exit_high or  # Exit breakout
                    current_high >= stop_loss):  # Stop loss
                    df.loc[df.index[i], 'signal'] = 1  # Buy signal (cover short)
                    current_position = 0
                    entry_price = None
                    stop_loss = None
                    position_size = 0
            
            df.loc[df.index[i], 'position'] = current_position
            df.loc[df.index[i], 'stop_loss'] = stop_loss
            df.loc[df.index[i], 'position_size'] = position_size
        
        # Convert signal column to Buy_Signal and Sell_Signal columns
        df['Buy_Signal'] = 0
        df['Sell_Signal'] = 0
        df.loc[df['signal'] == 1, 'Buy_Signal'] = 1
        df.loc[df['signal'] == -1, 'Sell_Signal'] = 1
        
        return df
    
    def visualize_results(self, results: Dict):
        """
        Visualizes the results of a backtest using Plotly for interactive charts.
        This method creates plots for direct display (not JSON serialization).
        """
        print(f"Turtle Breakout Strategy Results for {results.get('symbol', 'Unknown')}")
        print(f"Total Return: {results.get('total_return_pct', 0):.2f}%")
        print(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown: {results.get('max_drawdown_pct', 0):.2f}%")
    
    def get_json_visualizations(self, results: Dict) -> Dict[str, Any]:
        """
        Build two Plotly charts (JSON-serialised) for Turtle Breakout strategy.
        """
        df = results.get("data")
        if df is None or df.empty:
            raise ValueError("results['data'] must be a non-empty DataFrame.")

        # Handle MultiIndex columns - flatten them for easier access
        if isinstance(df.columns, pd.MultiIndex):
            new_columns = []
            for col in df.columns:
                if isinstance(col, tuple):
                    new_col = col[0] if col[0] else col[1] if len(col) > 1 else str(col)
                else:
                    new_col = col
                new_columns.append(new_col)
            df = df.copy()
            df.columns = new_columns

        # ── Price with turtle breakout levels ─────────────────────────────────────
        fig_price = go.Figure()

        # Price line (mandatory)
        if "Close" not in df.columns:
            raise KeyError("'Close' column is required for the price plot.")
        fig_price.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"],
                mode="lines",
                name="Close Price",
                line=dict(color='black', width=2)
            )
        )

        # Add breakout channels if available
        entry_period = results.get('parameters', {}).get('entry_period', self.entry_period)
        exit_period = results.get('parameters', {}).get('exit_period', self.exit_period)
        
        if 'Entry_High' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=df['Entry_High'], 
                    name=f"Entry High ({entry_period}d)", 
                    line=dict(color='blue', width=1, dash='dash')
                )
            )
            
        if 'Entry_Low' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=df['Entry_Low'], 
                    name=f"Entry Low ({entry_period}d)", 
                    line=dict(color='blue', width=1, dash='dash')
                )
            )
            
        if 'Exit_High' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=df['Exit_High'], 
                    name=f"Exit High ({exit_period}d)", 
                    line=dict(color='red', width=1, dash='dot')
                )
            )
            
        if 'Exit_Low' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=df['Exit_Low'], 
                    name=f"Exit Low ({exit_period}d)", 
                    line=dict(color='red', width=1, dash='dot')
                )
            )

        # Add ATR on secondary y-axis if available
        if 'ATR' in df.columns:
            atr_period = results.get('parameters', {}).get('atr_period', self.atr_period)
            fig_price.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=df['ATR'], 
                    name=f"ATR ({atr_period})", 
                    line=dict(color='purple', width=1.5),
                    yaxis='y2'
                )
            )

        # Buy / long markers
        if "Buy_Signal" in df.columns:
            buys = df["Buy_Signal"] == 1
            if buys.any():
                fig_price.add_trace(
                    go.Scatter(
                        x=df.index[buys],
                        y=df["Close"][buys],
                        mode="markers",
                        marker=dict(symbol='triangle-up', size=15, color='green'),
                        name="Buy Signal"
                    )
                )

        # Sell / short markers
        if "Sell_Signal" in df.columns:
            sells = df["Sell_Signal"] == 1
            if sells.any():
                fig_price.add_trace(
                    go.Scatter(
                        x=df.index[sells],
                        y=df["Close"][sells],
                        mode="markers",
                        marker=dict(symbol='triangle-down', size=15, color='red'),
                        name="Sell Signal"
                    )
                )

        fig_price.update_layout(
            title=None,
            xaxis_title=None,
            yaxis_title="Price ($)",
            yaxis2=dict(
                title="ATR ($)",
                overlaying='y',
                side='right'
            ),
            legend_orientation="h",
            template="plotly_white",
            margin=dict(l=40, r=20, t=35, b=35),
            showlegend=True,
            hovermode='x unified'
        )

        # ── Portfolio value curve ────────────────────────────────────────────────
        fig_port = go.Figure()
        if "Portfolio_Value" in df.columns:
            fig_port.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["Portfolio_Value"],
                    mode="lines",
                    name="Portfolio Value",
                    line=dict(color='green', width=2),
                    hovertemplate='Date: %{x}<br>Portfolio Value: $%{y:,.2f}<extra></extra>'
                )
            )
        else:
            fig_port.add_annotation(
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                text="No 'Portfolio_Value' column supplied",
                showarrow=False
            )

        fig_port.update_layout(
            title=None,
            xaxis_title=None,
            yaxis_title="Portfolio Value ($)",
            legend_orientation="h",
            template="plotly_white",
            margin=dict(l=40, r=20, t=35, b=35),
            showlegend=True,
            hovermode='x unified'
        )

        # ── Serialise for frontend consumption ─────────────────────────
        return {
            "price_and_signals": pio.to_json(fig_price, validate=False),
            "portfolio_value":   pio.to_json(fig_port, validate=False),
        }

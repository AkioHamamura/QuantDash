# Bollinger Band Breakout strategy implementation
"""
Bollinger Band Breakout Strategy

Key Concepts:
- Bollinger Bands: SMA ± (standard deviation * multiplier)
- Breakout signals when price moves outside bands
- Mean reversion vs trend continuation
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
from strategies.base_strategy_class import BaseStrategy
from backtesting.metrics import calculate_comprehensive_metrics


class BollingerBreakout(BaseStrategy):
    """
    Bollinger Band Breakout Strategy
    
    Strategy Logic:
    - Buy when price breaks ABOVE upper Bollinger Band (upward breakout)
    - Sell when price breaks BELOW lower Bollinger Band (downward breakout)
    - Optional: Close position when price returns to middle band (SMA)
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0, initial_cash: float = 100000):
        """
        Initialize strategy parameters
        
        Args:
            period: Period for moving average and standard deviation calculation
            std_dev: Standard deviation multiplier for bands
            initial_cash: Starting capital
        """
        super().__init__(name="Bollinger Band Breakout", initial_cash=initial_cash)
        self.period = period
        self.std_dev = std_dev
        
        # Store parameters for metrics calculation
        self.parameters = {
            'period': self.period,
            'std_dev': self.std_dev,
            'initial_cash': self.initial_cash
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on Bollinger Band breakouts
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional columns for signals and indicators
        """
        df = data.copy()
        
        # Calculate Bollinger Bands
        df['sma'] = df['Close'].rolling(window=self.period).mean()
        df['std'] = df['Close'].rolling(window=self.period).std()
        df['upper_band'] = df['sma'] + (df['std'] * self.std_dev)
        df['lower_band'] = df['sma'] - (df['std'] * self.std_dev)
        
        # Initialize signal columns
        df['signal'] = 0
        df['position'] = 0
        
        # Generate signals
        current_position = 0
        
        for i in range(1, len(df)):
            # Previous values
            prev_close = df['Close'].iloc[i-1]
            prev_upper = df['upper_band'].iloc[i-1]
            prev_lower = df['lower_band'].iloc[i-1]
            
            # Current values
            curr_close = df['Close'].iloc[i]
            curr_upper = df['upper_band'].iloc[i]
            curr_lower = df['lower_band'].iloc[i]
            curr_sma = df['sma'].iloc[i]
            
            # Skip if we don't have enough data for bands
            if pd.isna(curr_upper) or pd.isna(curr_lower):
                df.loc[df.index[i], 'position'] = current_position
                continue
            
            # Breakout signals
            if current_position == 0:  # No position
                # Buy signal: price breaks above upper band
                if prev_close <= prev_upper and curr_close > curr_upper:
                    df.loc[df.index[i], 'signal'] = 1  # Buy signal
                    current_position = 1
                # Sell signal: price breaks below lower band
                elif prev_close >= prev_lower and curr_close < curr_lower:
                    df.loc[df.index[i], 'signal'] = -1  # Sell signal
                    current_position = -1
            
            elif current_position == 1:  # Long position
                # Exit long: price returns to middle band or breaks lower band
                if curr_close < curr_sma or curr_close < curr_lower:
                    df.loc[df.index[i], 'signal'] = -1  # Sell signal
                    current_position = 0
            
            elif current_position == -1:  # Short position
                # Exit short: price returns to middle band or breaks upper band
                if curr_close > curr_sma or curr_close > curr_upper:
                    df.loc[df.index[i], 'signal'] = 1  # Buy signal
                    current_position = 0
            
            df.loc[df.index[i], 'position'] = current_position
        
        # Convert signal column to separate Buy_Signal and Sell_Signal columns
        df['Buy_Signal'] = 0   # Initialize
        df['Sell_Signal'] = 0  # Initialize
        
        # Set Buy_Signal where signal is 1
        df.loc[df['signal'] == 1, 'Buy_Signal'] = 1
        
        # Set Sell_Signal where signal is -1
        df.loc[df['signal'] == -1, 'Sell_Signal'] = 1
        
        return df
    
    def visualize_results(self, results: Dict):
        """
        Visualizes the results of a backtest using Plotly for interactive charts.
        This method creates plots for direct display (not JSON serialization).
        """
        # For now, we'll use the JSON visualizations method
        # In a full implementation, this would create interactive plots for direct display
        print(f"Bollinger Breakout Strategy Results for {results.get('symbol', 'Unknown')}")
        print(f"Total Return: {results.get('total_return_pct', 0):.2f}%")
        print(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown: {results.get('max_drawdown_pct', 0):.2f}%")
    
    def get_json_visualizations(self, results: Dict) -> Dict[str, Any]:
        """
        Build two Plotly charts (JSON-serialised) from the `results` structure.
        Returns price chart with Bollinger Bands and portfolio value chart.
        """
        df = results.get("data")
        if df is None or df.empty:
            raise ValueError("results['data'] must be a non-empty DataFrame.")

        # Handle MultiIndex columns if present
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

        # ── Price with Bollinger Bands and signals ───────────────────────────────
        fig_price = go.Figure()

        # Price line
        if "Close" not in df.columns:
            raise KeyError("'Close' column is required for the price plot.")
        fig_price.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"],
                mode="lines",
                name="Close Price",
                line=dict(color='blue', width=2)
            )
        )

        # Add Bollinger Bands if they exist
        if 'upper_band' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['upper_band'],
                    name='Upper Band',
                    line=dict(color='red', width=1, dash='dash'),
                    fill=None
                )
            )
        
        if 'lower_band' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['lower_band'],
                    name='Lower Band',
                    line=dict(color='red', width=1, dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(255,0,0,0.1)'
                )
            )
        
        if 'sma' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['sma'],
                    name=f'SMA ({self.period})',
                    line=dict(color='orange', width=1)
                )
            )

        # Buy signals
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

        # Sell signals
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

        # Return JSON serialized charts
        return {
            "price_and_signals": pio.to_json(fig_price, validate=False),
            "portfolio_value": pio.to_json(fig_port, validate=False),
        }

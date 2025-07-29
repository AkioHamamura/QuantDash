# Pair Trading Z-Score strategy implementation
"""
Pair Trading Strategy

Key Concepts:
- Statistical arbitrage between correlated assets
- Z-score: Standardized spread deviation
- Mean reversion: Expectation that spread returns to mean
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


class PairTrading(BaseStrategy):
    """
    Pair Trading Z-Score Strategy
    
    Strategy Logic:
    - Calculate spread between two assets
    - Standardize spread using rolling Z-score
    - Long/short when Z-score exceeds thresholds
    - Exit when Z-score returns to mean
    
    Note: This implementation uses a synthetic approach with one asset
    In practice, you would need two correlated assets
    """
    
    def __init__(self, lookback_period: int = 60, entry_threshold: float = 2.0, 
                 exit_threshold: float = 0.5, initial_cash: float = 100000):
        """
        Initialize strategy parameters
        
        Args:
            lookback_period: Period for calculating rolling statistics
            entry_threshold: Z-score threshold for entry signals
            exit_threshold: Z-score threshold for exit signals
            initial_cash: Starting capital
        """
        super().__init__(name="Pair Trading", initial_cash=initial_cash)
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        
        # Store parameters for metrics calculation
        self.parameters = {
            'lookback_period': self.lookback_period,
            'entry_threshold': self.entry_threshold,
            'exit_threshold': self.exit_threshold,
            'initial_cash': self.initial_cash
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on pair trading strategy
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional columns for signals and indicators
        """
        df = data.copy()
        
        # Create synthetic pair using price and its moving average
        # In practice, you would use two different but correlated assets
        df['asset1'] = df['Close']  # Primary asset
        df['asset2'] = df['Close'].rolling(window=20).mean()  # Synthetic correlated asset
        
        # Calculate spread
        df['spread'] = df['asset1'] - df['asset2']
        
        # Calculate rolling statistics for Z-score
        df['spread_mean'] = df['spread'].rolling(window=self.lookback_period).mean()
        df['spread_std'] = df['spread'].rolling(window=self.lookback_period).std()
        
        # Calculate Z-score
        df['z_score'] = (df['spread'] - df['spread_mean']) / df['spread_std']
        
        # Alternative approach: Use price vs its Bollinger Band center as proxy
        df['sma'] = df['Close'].rolling(window=self.lookback_period).mean()
        df['price_std'] = df['Close'].rolling(window=self.lookback_period).std()
        df['price_z_score'] = (df['Close'] - df['sma']) / df['price_std']
        
        # Use price Z-score as our main signal (more realistic for single asset)
        df['z_score'] = df['price_z_score']
        
        # Initialize signal columns
        df['signal'] = 0
        df['position'] = 0
        
        # Generate signals
        current_position = 0
        
        for i in range(self.lookback_period, len(df)):
            current_z = df['z_score'].iloc[i]
            
            # Skip if we don't have enough data
            if pd.isna(current_z):
                df.loc[df.index[i], 'position'] = current_position
                continue
            
            if current_position == 0:  # No position
                # Enter long when Z-score is very negative (oversold)
                if current_z <= -self.entry_threshold:
                    df.loc[df.index[i], 'signal'] = 1  # Buy signal
                    current_position = 1
                
                # Enter short when Z-score is very positive (overbought)
                elif current_z >= self.entry_threshold:
                    df.loc[df.index[i], 'signal'] = -1  # Sell signal
                    current_position = -1
            
            elif current_position == 1:  # Long position
                # Exit long when Z-score returns to neutral or becomes positive
                if current_z >= self.exit_threshold:
                    df.loc[df.index[i], 'signal'] = -1  # Sell signal
                    current_position = 0
            
            elif current_position == -1:  # Short position
                # Exit short when Z-score returns to neutral or becomes negative
                if current_z <= -self.exit_threshold:
                    df.loc[df.index[i], 'signal'] = 1  # Buy signal (cover short)
                    current_position = 0
            
            df.loc[df.index[i], 'position'] = current_position
        
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
        print(f"Pair Trading Strategy Results for {results.get('symbol', 'Unknown')}")
        print(f"Total Return: {results.get('total_return_pct', 0):.2f}%")
        print(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown: {results.get('max_drawdown_pct', 0):.2f}%")
    
    def get_json_visualizations(self, results: Dict) -> Dict[str, Any]:
        """
        Build two Plotly charts (JSON-serialised) for Pair Trading strategy.
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

        # ── Price with pair trading signals ─────────────────────────────────────
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

        # Add moving average if available
        if 'SMA' in df.columns:
            lookback_period = results.get('parameters', {}).get('lookback_period', self.lookback_period)
            fig_price.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=df['SMA'], 
                    name=f"SMA ({lookback_period})", 
                    line=dict(color='orange', width=1.5)
                )
            )

        # Add Z-Score on secondary y-axis if available
        if 'Z_Score' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=df['Z_Score'], 
                    name="Z-Score", 
                    line=dict(color='purple', width=1.5),
                    yaxis='y2'
                )
            )
            
            # Add threshold lines for Z-Score
            entry_threshold = results.get('parameters', {}).get('entry_threshold', self.entry_threshold)
            exit_threshold = results.get('parameters', {}).get('exit_threshold', self.exit_threshold)
            
            fig_price.add_hline(y=entry_threshold, line_dash="dash", line_color="red", 
                              annotation_text=f"Entry (+{entry_threshold})", 
                              annotation_position="top right")
            fig_price.add_hline(y=-entry_threshold, line_dash="dash", line_color="red", 
                              annotation_text=f"Entry (-{entry_threshold})",
                              annotation_position="bottom right")
            fig_price.add_hline(y=exit_threshold, line_dash="dot", line_color="orange", 
                              annotation_text=f"Exit (+{exit_threshold})",
                              annotation_position="top right") 
            fig_price.add_hline(y=-exit_threshold, line_dash="dot", line_color="orange", 
                              annotation_text=f"Exit (-{exit_threshold})",
                              annotation_position="bottom right")

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
                title="Z-Score",
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

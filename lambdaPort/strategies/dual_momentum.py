# Dual Momentum strategy implementation
"""
Dual Momentum Strategy

Key Concepts:
- Relative momentum: Asset performance vs benchmark
- Absolute momentum: Asset performance vs risk-free rate
- Time series momentum: Recent performance trends
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


class DualMomentum(BaseStrategy):
    """
    Dual Momentum Strategy
    
    Strategy Logic:
    - Calculate relative momentum (asset vs benchmark)
    - Calculate absolute momentum (asset vs risk-free rate)
    - Buy when both momentum signals are positive
    - Sell when either momentum signal turns negative
    """
    
    def __init__(self, lookback_period: int = 60, risk_free_rate: float = 0.02, initial_cash: float = 100000):
        """
        Initialize strategy parameters
        
        Args:
            lookback_period: Period for momentum calculation (days)
            risk_free_rate: Annual risk-free rate for absolute momentum
            initial_cash: Starting capital
        """
        super().__init__(name="Dual Momentum", initial_cash=initial_cash)
        self.lookback_period = lookback_period
        self.risk_free_rate = risk_free_rate
        
        # Store parameters for metrics calculation
        self.parameters = {
            'lookback_period': self.lookback_period,
            'risk_free_rate': self.risk_free_rate,
            'initial_cash': self.initial_cash
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on dual momentum
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional columns for signals and indicators
        """
        df = data.copy()
        
        # Calculate returns
        df['returns'] = df['Close'].pct_change()
        
        # Calculate rolling momentum (cumulative returns over lookback period)
        df['momentum'] = df['returns'].rolling(window=self.lookback_period).apply(
            lambda x: (1 + x).prod() - 1, raw=True
        )
        
        # Calculate absolute momentum (vs risk-free rate)
        # Convert annual risk-free rate to daily
        daily_risk_free = (1 + self.risk_free_rate) ** (1/252) - 1
        risk_free_return = daily_risk_free * self.lookback_period
        df['absolute_momentum'] = df['momentum'] - risk_free_return
        
        # For relative momentum, we'll use a simple benchmark (market trend)
        # In practice, this could be SPY, market index, or sector ETF
        df['sma_long'] = df['Close'].rolling(window=self.lookback_period).mean()
        df['sma_short'] = df['Close'].rolling(window=self.lookback_period // 2).mean()
        df['relative_momentum'] = (df['sma_short'] - df['sma_long']) / df['sma_long']
        
        # Initialize signal columns
        df['signal'] = 0
        df['position'] = 0
        
        # Generate signals
        current_position = 0
        
        for i in range(self.lookback_period, len(df)):
            # Get current momentum values
            absolute_mom = df['absolute_momentum'].iloc[i]
            relative_mom = df['relative_momentum'].iloc[i]
            
            # Skip if we don't have enough data
            if pd.isna(absolute_mom) or pd.isna(relative_mom):
                df.loc[df.index[i], 'position'] = current_position
                continue
            
            # Dual momentum signals
            if current_position == 0:  # No position
                # Buy when both momentum signals are positive
                if absolute_mom > 0 and relative_mom > 0:
                    df.loc[df.index[i], 'signal'] = 1  # Buy signal
                    current_position = 1
            
            elif current_position == 1:  # Long position
                # Sell when either momentum signal turns negative
                if absolute_mom <= 0 or relative_mom <= 0:
                    df.loc[df.index[i], 'signal'] = -1  # Sell signal
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
        print(f"Dual Momentum Strategy Results for {results.get('symbol', 'Unknown')}")
        print(f"Total Return: {results.get('total_return_pct', 0):.2f}%")
        print(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown: {results.get('max_drawdown_pct', 0):.2f}%")
    
    def get_json_visualizations(self, results: Dict) -> Dict[str, Any]:
        """
        Build two Plotly charts (JSON-serialised) for Dual Momentum strategy.
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

        # ── Price with momentum signals ───────────────────────────────────────────
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

        # Add momentum indicators if they exist
        if 'Absolute_Momentum' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=df['Absolute_Momentum'], 
                    name=f"Absolute Momentum ({results.get('parameters', {}).get('lookback_period', 'N/A')} days)", 
                    line=dict(color='blue', width=1.5),
                    yaxis='y2'
                )
            )
            
        if 'Relative_Momentum' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=df['Relative_Momentum'], 
                    name="Relative Momentum", 
                    line=dict(color='orange', width=1.5),
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
                title="Momentum",
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

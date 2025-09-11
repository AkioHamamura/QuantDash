# RSI Pullback strategy implementation
"""
RSI Pullback Strategy

Key Concepts:
- RSI (Relative Strength Index): Momentum oscillator (0-100)
- Oversold/Overbought conditions: RSI < 30 / RSI > 70
- Trend following with pullback entries
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


class RSIPullback(BaseStrategy):
    """
    RSI Pullback Strategy
    
    Strategy Logic:
    - Identify trend direction using moving average
    - Buy on RSI oversold pullbacks in uptrend
    - Sell on RSI overbought rallies in downtrend
    - Exit when RSI reaches opposite extreme
    """
    
    def __init__(self, rsi_period: int = 14, ma_period: int = 50, 
                 oversold: int = 30, overbought: int = 70, initial_cash: float = 100000):
        """
        Initialize strategy parameters
        
        Args:
            rsi_period: Period for RSI calculation
            ma_period: Period for trend identification moving average
            oversold: RSI oversold threshold
            overbought: RSI overbought threshold
            initial_cash: Starting capital
        """
        super().__init__(name="RSI Pullback", initial_cash=initial_cash)
        self.rsi_period = rsi_period
        self.ma_period = ma_period
        self.oversold = oversold
        self.overbought = overbought
        
        # Store parameters for metrics calculation
        self.parameters = {
            'rsi_period': self.rsi_period,
            'ma_period': self.ma_period,
            'oversold': self.oversold,
            'overbought': self.overbought,
            'initial_cash': self.initial_cash
        }
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices: Series of prices
            period: Calculation period
            
        Returns:
            Series with RSI values
        """
        delta = prices.diff().dropna()
        
        # Calculate gains and losses
        gains = delta.clip(lower=0)  # Keep positive values, set negative to 0
        losses = (-delta).clip(lower=0)  # Keep negative values (as positive), set positive to 0
        
        # Calculate rolling averages
        avg_gain = gains.rolling(window=period).mean()
        avg_loss = losses.rolling(window=period).mean()
        
        # Calculate RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Reindex to match original prices index
        return rsi.reindex(prices.index)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on RSI pullback strategy
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional columns for signals and indicators
        """
        df = data.copy()
        
        # Calculate RSI
        df['rsi'] = self.calculate_rsi(df['Close'], self.rsi_period)
        
        # Calculate trend indicator (moving average)
        df['ma'] = df['Close'].rolling(window=self.ma_period).mean()
        df['trend'] = np.where(df['Close'] > df['ma'], 'up', 'down')
        
        # Initialize signal columns
        df['signal'] = 0
        df['position'] = 0
        
        # Generate signals
        current_position = 0
        
        for i in range(max(self.rsi_period, self.ma_period), len(df)):
            current_rsi = df['rsi'].iloc[i]
            current_trend = df['trend'].iloc[i]
            current_close = df['Close'].iloc[i]
            current_ma = df['ma'].iloc[i]
            
            # Skip if we don't have enough data
            if pd.isna(current_rsi) or pd.isna(current_ma):
                df.loc[df.index[i], 'position'] = current_position
                continue
            
            if current_position == 0:  # No position
                # Buy on oversold pullback in uptrend
                if (current_trend == 'up' and 
                    current_rsi <= self.oversold and
                    current_close > current_ma):
                    df.loc[df.index[i], 'signal'] = 1  # Buy signal
                    current_position = 1
                
                # Sell on overbought rally in downtrend
                elif (current_trend == 'down' and 
                      current_rsi >= self.overbought and
                      current_close < current_ma):
                    df.loc[df.index[i], 'signal'] = -1  # Sell signal
                    current_position = -1
            
            elif current_position == 1:  # Long position
                # Exit long when RSI becomes overbought or trend changes
                if (current_rsi >= self.overbought or 
                    current_trend == 'down'):
                    df.loc[df.index[i], 'signal'] = -1  # Sell signal
                    current_position = 0
            
            elif current_position == -1:  # Short position
                # Exit short when RSI becomes oversold or trend changes
                if (current_rsi <= self.oversold or 
                    current_trend == 'up'):
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
        print(f"RSI Pullback Strategy Results for {results.get('symbol', 'Unknown')}")
        print(f"Total Return: {results.get('total_return_pct', 0):.2f}%")
        print(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown: {results.get('max_drawdown_pct', 0):.2f}%")
    
    def get_json_visualizations(self, results: Dict) -> Dict[str, Any]:
        """
        Build two Plotly charts (JSON-serialised) for RSI Pullback strategy.
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

        # ── Price with RSI signals ──────────────────────────────────────────────
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
        if 'MA' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=df['MA'], 
                    name=f"MA ({results.get('parameters', {}).get('ma_period', 'N/A')})", 
                    line=dict(color='orange', width=1.5)
                )
            )

        # Add RSI on secondary y-axis
        if 'RSI' in df.columns:
            fig_price.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=df['RSI'], 
                    name=f"RSI ({results.get('parameters', {}).get('rsi_period', 'N/A')})", 
                    line=dict(color='purple', width=1.5),
                    yaxis='y2'
                )
            )
            
            # Add RSI levels on secondary axis
            overbought = results.get('parameters', {}).get('overbought', 70)
            oversold = results.get('parameters', {}).get('oversold', 30)
            
            fig_price.add_hline(y=overbought, line_dash="dash", line_color="red", 
                              annotation_text=f"Overbought ({overbought})", 
                              annotation_position="top right")
            fig_price.add_hline(y=oversold, line_dash="dash", line_color="green", 
                              annotation_text=f"Oversold ({oversold})",
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
                title="RSI",
                overlaying='y',
                side='right',
                range=[0, 100]
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

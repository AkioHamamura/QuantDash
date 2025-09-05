# Mean-Reverting Gap Fade strategy implementation
"""
Gap Fade Strategy

Key Concepts:
- Price gaps: Significant overnight price movements
- Mean reversion: Expectation that gaps will fill
- Risk management: Stop losses for failed fades
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


class GapFade(BaseStrategy):
    """
    Gap Fade Strategy
    
    Strategy Logic:
    - Identify significant price gaps (open vs previous close)
    - Fade gaps by trading in opposite direction
    - Exit when gap fills or stop loss is hit
    """
    
    def __init__(self, gap_threshold: float = 0.02, stop_loss: float = 0.05, initial_cash: float = 100000):
        """
        Initialize strategy parameters
        
        Args:
            gap_threshold: Minimum gap size as percentage to trigger signal
            stop_loss: Stop loss percentage from entry price
            initial_cash: Starting capital
        """
        super().__init__(name="Gap Fade", initial_cash=initial_cash)
        self.gap_threshold = gap_threshold
        self.stop_loss = stop_loss
        
        # Store parameters for metrics calculation
        self.parameters = {
            'gap_threshold': self.gap_threshold,
            'stop_loss': self.stop_loss,
            'initial_cash': self.initial_cash
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on gap fade strategy
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional columns for signals and indicators
        """
        df = data.copy()
        
                # Calculate gap from previous day's close to current day's open
        df['prev_close'] = df['Close'].shift(1)
        df['gap_size'] = (df['Open'] - df['prev_close']) / df['prev_close']
        df['gap_direction'] = np.where(df['gap_size'] > 0, 'up', 'down')
        
        # Calculate average true range for volatility context
        df['high_low'] = df['High'] - df['Low']
        df['high_close'] = abs(df['High'] - df['prev_close'])
        df['low_close'] = abs(df['Low'] - df['prev_close'])
        df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['true_range'].rolling(window=14).mean()
        
        # Initialize signal columns
        df['signal'] = 0
        df['position'] = 0
        df['entry_price'] = np.nan
        df['stop_loss_price'] = np.nan
        df['target_price'] = np.nan
        
        # Generate signals
        current_position = 0
        entry_price = None
        stop_loss_price = None
        target_price = None
        
        for i in range(1, len(df)):
            current_gap = df['gap_size'].iloc[i]
            current_open = df['Open'].iloc[i]
            current_close = df['Close'].iloc[i]
            current_high = df['High'].iloc[i]
            current_low = df['Low'].iloc[i]
            prev_close = df['prev_close'].iloc[i]
            
            # Skip if we don't have enough data
            if pd.isna(current_gap) or pd.isna(prev_close):
                df.loc[df.index[i], 'position'] = current_position
                continue
            
            if current_position == 0:  # No position
                # Look for significant gaps to fade
                if abs(current_gap) >= self.gap_threshold:
                    if current_gap > 0:  # Gap up - short the stock
                        df.loc[df.index[i], 'signal'] = -1  # Sell signal
                        current_position = -1
                        entry_price = current_open
                        stop_loss_price = entry_price * (1 + self.stop_loss)
                        target_price = prev_close  # Target is gap fill
                    
                    elif current_gap < 0:  # Gap down - go long
                        df.loc[df.index[i], 'signal'] = 1  # Buy signal
                        current_position = 1
                        entry_price = current_open
                        stop_loss_price = entry_price * (1 - self.stop_loss)
                        target_price = prev_close  # Target is gap fill
                    
                    # Store entry details
                    df.loc[df.index[i], 'entry_price'] = entry_price
                    df.loc[df.index[i], 'stop_loss_price'] = stop_loss_price
                    df.loc[df.index[i], 'target_price'] = target_price
            
            elif current_position == 1:  # Long position
                # Check for exit conditions
                if (current_low <= stop_loss_price or  # Stop loss hit
                    current_high >= target_price):      # Target reached (gap filled)
                    df.loc[df.index[i], 'signal'] = -1  # Sell signal
                    current_position = 0
                    entry_price = None
                    stop_loss_price = None
                    target_price = None
            
            elif current_position == -1:  # Short position
                # Check for exit conditions
                if (current_high >= stop_loss_price or  # Stop loss hit
                    current_low <= target_price):       # Target reached (gap filled)
                    df.loc[df.index[i], 'signal'] = 1  # Buy signal (cover short)
                    current_position = 0
                    entry_price = None
                    stop_loss_price = None
                    target_price = None
            
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
        print(f"Gap Fade Strategy Results for {results.get('symbol', 'Unknown')}")
        print(f"Total Return: {results.get('total_return_pct', 0):.2f}%")
        print(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown: {results.get('max_drawdown_pct', 0):.2f}%")
    
    def get_json_visualizations(self, results: Dict) -> Dict[str, Any]:
        """
        Build two Plotly charts (JSON-serialised) for Gap Fade strategy.
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

        # ── Price with gap signals ─────────────────────────────────────────────
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

        # Add gap markers if they exist
        if 'Gap_Size' in df.columns:
            # Mark significant gaps above threshold
            threshold = results.get('parameters', {}).get('gap_threshold', self.gap_threshold)
            significant_gaps = df[abs(df['Gap_Size']) >= threshold]
            
            if not significant_gaps.empty:
                # Gap up markers
                gap_ups = significant_gaps[significant_gaps['Gap_Size'] > 0]
                if not gap_ups.empty:
                    fig_price.add_trace(
                        go.Scatter(
                            x=gap_ups.index,
                            y=gap_ups['Close'],
                            mode="markers",
                            marker=dict(symbol='diamond', size=12, color='orange'),
                            name=f"Gap Up (>{threshold*100:.1f}%)"
                        )
                    )
                
                # Gap down markers
                gap_downs = significant_gaps[significant_gaps['Gap_Size'] < 0]
                if not gap_downs.empty:
                    fig_price.add_trace(
                        go.Scatter(
                            x=gap_downs.index,
                            y=gap_downs['Close'],
                            mode="markers",
                            marker=dict(symbol='diamond', size=12, color='purple'),
                            name=f"Gap Down (<-{threshold*100:.1f}%)"
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

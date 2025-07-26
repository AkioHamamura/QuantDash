# Moving Average Crossover strategy implementation
"""
LEARNING GUIDE: Building a Trading Strategy from Scratch

Key Concepts:
- DataFrame.iterrows() for chronological processing
- Rolling windows for moving averages
- State management for position tracking
- Performance calculation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
import os
from strategies.base_strategy_class import BaseStrategy
from backtesting.metrics import calculate_comprehensive_metrics


class MovingAverageCrossover(BaseStrategy):
    """
    Moving Average Crossover Strategy
    
    Strategy Logic:
    - Buy when fast Moving average (average for the last x days) crosses ABOVE slow Moving average (Golden Cross)
    - Sell when fast Moving average crosses BELOW slow Moving average (Death Cross)
    """
    
    # Initialize strategy parameters. For MA strategy: defining fast and slow periods.
    def __init__(self, fast_period: int = 10, slow_period: int = 30, initial_cash: float = 100000):
        """
        Initialize strategy parameters
        
        Args:
            fast_period: Period for fast moving average (e.g., 10 days)
            slow_period: Period for slow moving average (e.g., 30 days)
            initial_cash: Starting capital
        """
        super().__init__(initial_cash=initial_cash)  # Call parent constructor with initial_cash
        self.fast_period = fast_period
        self.slow_period = slow_period
        
        # Store parameters for metrics calculation
        self.parameters = {
            'fast_period': self.fast_period,
            'slow_period': self.slow_period
        }
        
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        STEP 2: Generate buy/sell signals (REQUIRED by BaseStrategy)
        
        Calculate moving averages and crossover signals.
        
        Returns:
            DataFrame with added columns:
            - MA_Fast: Fast moving average
            - MA_Slow: Slow moving average  
            - Buy_Signal: 1 when golden cross occurs, 0 otherwise
            - Sell_Signal: 1 when death cross occurs, 0 otherwise
        """
        df = data.copy() # Create a copy to avoid modifying original data

        # Calculate moving averages at close prices
        df['MA_Fast'] = df['Close'].rolling(window=self.fast_period).mean() # Create Fast MA column in DataFrame
        df['MA_Slow'] = df['Close'].rolling(window=self.slow_period).mean() # Create Slow MA column in DataFrame
        
        # Calculate crossover signals
        # 1 when fast MA > slow MA, 0 otherwise
        df['Fast_Above_Slow'] = (df['MA_Fast'] > df['MA_Slow']).astype(int) # binary column for fast above slow
        
        # Detect crossovers: difference between current and previous signal
        df['Signal_Change'] = df['Fast_Above_Slow'].diff() # 1 when fast crosses above slow, -1 when fast crosses below slow
        
        # Generate explicit buy/sell signals
        df['Buy_Signal'] = 0   # Initialize
        df['Sell_Signal'] = 0  # Initialize
        
        # Signal_Change = 1 means golden cross (fast MA crossed above slow MA)
        # locates where Signal_Change is 1 and sets Buy_Signal to 1
        df.loc[df['Signal_Change'] == 1, 'Buy_Signal'] = 1
        
        # Signal_Change = -1 means death cross (fast MA crossed below slow MA)  
        # locates where Signal_Change is -1 and sets Sell_Signal to 1
        df.loc[df['Signal_Change'] == -1, 'Sell_Signal'] = 1
        
        print(df)  # Print rows for debugging <---------------
        return df


    def visualize_results(self, results: Dict):
        """
        Visualizes the results of a backtest using Plotly for interactive charts.

        Parameters:
        backtest_results (dict): A dictionary containing backtest results
        """
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        import pandas as pd
        
        # Debug: Print the structure of backtest_results
        print("=== DEBUG: Backtest Results Structure ===")
        print(f"Keys in backtest_results: {list(results.keys())}")
        
        # Create subplots: stock price + signals, portfolio value, metrics table
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Stock Price & Trading Signals', 'Portfolio Value', 'Performance Metrics'),
            vertical_spacing=0.12,
            row_heights=[0.5, 0.25, 0.25],
            shared_xaxes=True,
            specs=[[{"type": "scatter"}],
                [{"type": "scatter"}],
                [{"type": "table"}]]
        )
        
        data = results['data']
        print(f"Data shape: {data.shape}")
        print(f"Data columns: {list(data.columns)}")
        print(f"Data index type: {type(data.index)}")
        print(f"First few rows:\n{data.head()}")
        
        # Check if we have the required columns
        required_cols = ['Close', 'Buy_Signal', 'Sell_Signal', 'Portfolio_Value']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            print(f"WARNING: Missing columns: {missing_cols}")
        
        # Handle MultiIndex columns - flatten them for easier access
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten MultiIndex columns by taking the first level that's not empty
            new_columns = []
            for col in data.columns:
                if isinstance(col, tuple):
                    # Take the first non-empty part of the tuple
                    new_col = col[0] if col[0] else col[1] if len(col) > 1 else str(col)
                else:
                    new_col = col
                new_columns.append(new_col)
            data.columns = new_columns
            print(f"Flattened columns to: {list(data.columns)}")
        
        # 1. Stock Price with Moving Averages - Add some debug info
        try:
            close_data = data['Close']
            print(f"Close data shape: {close_data.shape}, first value: {close_data.iloc[0] if len(close_data) > 0 else 'EMPTY'}")
            
            fig.add_trace(
                go.Scatter(x=data.index, y=data['Close'], name='Close Price', 
                        line=dict(color='black', width=2)),
                row=1, col=1
            )
            print("✓ Added Close Price trace")
        except Exception as e:
            print(f"ERROR adding Close Price: {e}")
        
        # Add Moving Averages if they exist
        if 'MA_Fast' in data.columns:
            try:
                fig.add_trace(
                    go.Scatter(x=data.index, y=data['MA_Fast'], 
                            name=f"MA Fast ({results['parameters']['fast_period']})", 
                            line=dict(color='blue', width=1.5)),
                    row=1, col=1
                )
                print("✓ Added MA Fast trace")
            except Exception as e:
                print(f"ERROR adding MA Fast: {e}")
        
        if 'MA_Slow' in data.columns:
            try:
                fig.add_trace(
                    go.Scatter(x=data.index, y=data['MA_Slow'], 
                            name=f"MA Slow ({results['parameters']['slow_period']})", 
                            line=dict(color='red', width=1.5)),
                    row=1, col=1
                )
                print("✓ Added MA Slow trace")
            except Exception as e:
                print(f"ERROR adding MA Slow: {e}")
        
        # 2. Buy/Sell Signals with debugging
        try:
            # Debug signal data
            buy_signal_count = (data['Buy_Signal'] == 1).sum() if 'Buy_Signal' in data.columns else 0
            sell_signal_count = (data['Sell_Signal'] == 1).sum() if 'Sell_Signal' in data.columns else 0
            print(f"Buy signals found: {buy_signal_count}")
            print(f"Sell signals found: {sell_signal_count}")
            
            if 'Buy_Signal' in data.columns:
                buy_signals = data[data['Buy_Signal'] == 1]
                print(f"Buy signals shape: {buy_signals.shape}")
                if not buy_signals.empty:
                    print(f"Buy signal dates: {buy_signals.index.tolist()}")
            
            if 'Sell_Signal' in data.columns:
                sell_signals = data[data['Sell_Signal'] == 1]
                print(f"Sell signals shape: {sell_signals.shape}")
                if not sell_signals.empty:
                    print(f"Sell signal dates: {sell_signals.index.tolist()}")
            
            # Get trade information
            trades = results.get('trades', [])
            print(f"Number of trades: {len(trades)}")
            
            # Add buy signals
            if 'Buy_Signal' in data.columns:
                buy_signals = data[data['Buy_Signal'] == 1]
                print(f"Buy signals shape: {buy_signals.shape}")
                if not buy_signals.empty:
                    print(f"Buy signal dates: {buy_signals.index.tolist()}")
                    
                    # Create hover text with trade information
                    buy_hover_text = []
                    trade_idx = 0
                    for date, row in buy_signals.iterrows():
                        close_price = float(row['Close'])
                        
                        # Try to match with trade data for share information
                        shares_info = ""
                        if trade_idx < len(trades):
                            trade = trades[trade_idx]
                            # Check if the dates are close (within a few days)
                            if trade.entry_date and abs((trade.entry_date - date).days) <= 3:
                                shares_info = f"<br>Shares Bought: {trade.shares}"
                                trade_idx += 1
                        
                        buy_hover_text.append(f"Date: {date.strftime('%Y-%m-%d')}<br>Price: ${close_price:.2f}{shares_info}<br>BUY SIGNAL")
                    
                    fig.add_trace(
                        go.Scatter(x=buy_signals.index, y=buy_signals['Close'], 
                                mode='markers', name='Buy Signal',
                                marker=dict(symbol='triangle-up', size=15, color='green'),
                                hovertemplate='%{customdata}<extra></extra>',
                                customdata=buy_hover_text),
                        row=1, col=1
                    )
                    print("✓ Added Buy Signal markers")
            
            # Add sell signals
            if 'Sell_Signal' in data.columns:
                sell_signals = data[data['Sell_Signal'] == 1]
                print(f"Sell signals shape: {sell_signals.shape}")
                if not sell_signals.empty:
                    print(f"Sell signal dates: {sell_signals.index.tolist()}")
                    
                    # Create hover text with trade information
                    sell_hover_text = []
                    completed_trades = [t for t in trades if t.exit_date is not None]
                    trade_idx = 0
                    for date, row in sell_signals.iterrows():
                        close_price = float(row['Close'])
                        
                        # Try to match with completed trade data
                        shares_info = ""
                        profit_info = ""
                        if trade_idx < len(completed_trades):
                            trade = completed_trades[trade_idx]
                            # Check if the dates are close (within a few days)
                            if trade.exit_date and abs((trade.exit_date - date).days) <= 3:
                                shares_info = f"<br>Shares Sold: {trade.shares}"
                                profit_info = f"<br>Profit/Loss: ${trade.profit_loss:.2f}"
                                trade_idx += 1
                        
                        sell_hover_text.append(f"Date: {date.strftime('%Y-%m-%d')}<br>Price: ${close_price:.2f}{shares_info}{profit_info}<br>SELL SIGNAL")
                    
                    fig.add_trace(
                        go.Scatter(x=sell_signals.index, y=sell_signals['Close'], 
                                mode='markers', name='Sell Signal',
                                marker=dict(symbol='triangle-down', size=15, color='red'),
                                hovertemplate='%{customdata}<extra></extra>',
                                customdata=sell_hover_text),
                        row=1, col=1
                    )
                    print("✓ Added Sell Signal markers")
                
        except Exception as e:
            print(f"ERROR adding signals: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Portfolio Value
        try:
            if 'Portfolio_Value' in data.columns:
                fig.add_trace(
                    go.Scatter(x=data.index, y=data['Portfolio_Value'], name='Portfolio Value', 
                            line=dict(color='green', width=2),
                            hovertemplate='Date: %{x}<br>Portfolio Value: $%{y:,.2f}<extra></extra>'),
                    row=2, col=1
                )
                print("✓ Added Portfolio Value trace")
            else:
                print("WARNING: Portfolio_Value column not found")
        except Exception as e:
            print(f"ERROR adding Portfolio Value: {e}")
        
        # 4. Performance Metrics Table
        try:
            # Prepare metrics data for the table
            metrics_data = {
                'Metric': [
                    'Strategy',
                    'Initial Cash',
                    'Final Value',
                    'Total Return (%)',
                    'Total Trades',
                    'Winning Trades',
                    'Win Rate (%)',
                    'Sharpe Ratio',
                    'Sortino Ratio',
                    'Max Drawdown (%)',
                    'Volatility (%)'
                ],
                'Value': [
                    results.get('strategy', 'N/A'),
                    f"${results.get('initial_cash', 0):,.2f}",
                    f"${results.get('final_value', 0):,.2f}",
                    f"{results.get('total_return_pct', 0):.2f}%",
                    str(results.get('total_trades', 0)),
                    str(results.get('winning_trades', 0)),
                    f"{results.get('win_rate_pct', 0):.1f}%",
                    f"{results.get('sharpe_ratio', 0):.3f}",
                    f"{results.get('sortino_ratio', 0):.3f}",
                    f"{results.get('max_drawdown_pct', 0):.2f}%",
                    f"{results.get('volatility_pct', 0):.2f}%"
                ]
            }
            
            # Add strategy parameters if available
            if 'parameters' in results:
                params = results['parameters']
                if 'fast_period' in params and 'slow_period' in params:
                    metrics_data['Metric'].insert(1, 'Parameters')
                    metrics_data['Value'].insert(1, f"Fast MA: {params['fast_period']}, Slow MA: {params['slow_period']}")
            
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=['<b>Metric</b>', '<b>Value</b>'],
                        fill_color='lightblue',
                        align='left',
                        font=dict(color='white', size=12),
                        height=30
                    ),
                    cells=dict(
                        values=[metrics_data['Metric'], metrics_data['Value']],
                        fill_color=[['white', 'lightgray'] * len(metrics_data['Metric'])],
                        align='left',
                        font=dict(color='black', size=11),
                        height=25
                    )
                ),
                row=3, col=1
            )
            print("✓ Added Performance Metrics table")
        except Exception as e:
            print(f"ERROR adding metrics table: {e}")
            import traceback
            traceback.print_exc()
        
        # Update layout
        fig.update_layout(
            title=f"Backtest Results: {results.get('strategy', 'Unknown Strategy')}",
            height=1000,  # Increased height to accommodate the metrics table
            showlegend=True,
            template='plotly_white',
            hovermode='x unified'
        )
        
        # Update y-axes
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Portfolio Value ($)", row=2, col=1)
        
        # Update x-axes
        fig.update_xaxes(title_text="Date", row=2, col=1)
        
        print("=== DEBUG: Showing plot ===")
        
        # Show the plot
        fig.show()
        
        return fig








def visualize_backtest_results(backtest_results):
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
    print(f"Keys in backtest_results: {list(backtest_results.keys())}")
    
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
    
    data = backtest_results['data']
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
                          name=f"MA Fast ({backtest_results['parameters']['fast_period']})", 
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
                          name=f"MA Slow ({backtest_results['parameters']['slow_period']})", 
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
        trades = backtest_results.get('trades', [])
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
                backtest_results.get('strategy', 'N/A'),
                f"${backtest_results.get('initial_cash', 0):,.2f}",
                f"${backtest_results.get('final_value', 0):,.2f}",
                f"{backtest_results.get('total_return_pct', 0):.2f}%",
                str(backtest_results.get('total_trades', 0)),
                str(backtest_results.get('winning_trades', 0)),
                f"{backtest_results.get('win_rate_pct', 0):.1f}%",
                f"{backtest_results.get('sharpe_ratio', 0):.3f}",
                f"{backtest_results.get('sortino_ratio', 0):.3f}",
                f"{backtest_results.get('max_drawdown_pct', 0):.2f}%",
                f"{backtest_results.get('volatility_pct', 0):.2f}%"
            ]
        }
        
        # Add strategy parameters if available
        if 'parameters' in backtest_results:
            params = backtest_results['parameters']
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
        title=f"Backtest Results: {backtest_results.get('strategy', 'Unknown Strategy')}",
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
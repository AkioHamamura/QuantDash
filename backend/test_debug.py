#!/usr/bin/env python3

import sys
import os

# Add the backend/src directory to Python path for imports
backend_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if backend_src_path not in sys.path:
    sys.path.insert(0, backend_src_path)

# Also add the backend directory to path
backend_path = os.path.abspath(os.path.dirname(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from backtesting.engine import BacktestEngine
from strategies.ma_crossover import MovingAverageCrossover
from data.data_fetcher import fetch_stock_data

def test_visualization_data():
    print("Testing visualization data flow...")
    
    # Try to load cached data directly
    print("1. Loading cached data...")
    import pandas as pd
    
    # Try to load existing cached AAPL data
    cache_file = "/Users/jakobildstad/Dev/QuantDash/backend/cache/AAPL_1y_None_None_1d_data.parquet"
    if os.path.exists(cache_file):
        data = pd.read_parquet(cache_file)
        print(f"  SUCCESS: Loaded {len(data)} rows from cache")
    else:
        print("  Trying to fetch with cache...")
        data = fetch_stock_data("AMZN", period="1y", use_cache=True)  # Try AMZN which should be cached
        if data is None or data.empty:
            print("  FAILED: No data found")
            return
        print(f"  SUCCESS: Got {len(data)} rows of data")
    print(f"  Columns: {list(data.columns)}")
    print(f"  Date range: {data.index.min()} to {data.index.max()}")
    
    # Create strategy
    print("\n2. Creating strategy...")
    strategy = MovingAverageCrossover(
        fast_period=12,
        slow_period=26,
        initial_cash=10000
    )
    
    # Run backtest
    print("\n3. Running backtest...")
    engine = BacktestEngine(strategy)
    results, viz = engine.run(data, visualize=True)
    
    print(f"\n4. Results summary:")
    print(f"  Results type: {type(results)}")
    print(f"  Results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
    
    if 'data' in results:
        df = results['data']
        print(f"\n5. Data in results:")
        print(f"  DataFrame shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        
        # Check for moving averages
        if 'MA_Fast' in df.columns:
            non_nan_fast = df['MA_Fast'].dropna()
            print(f"  MA_Fast: {len(non_nan_fast)} non-NaN values, range: {non_nan_fast.min():.2f} to {non_nan_fast.max():.2f}")
        else:
            print("  MA_Fast: MISSING!")
            
        if 'MA_Slow' in df.columns:
            non_nan_slow = df['MA_Slow'].dropna()
            print(f"  MA_Slow: {len(non_nan_slow)} non-NaN values, range: {non_nan_slow.min():.2f} to {non_nan_slow.max():.2f}")
        else:
            print("  MA_Slow: MISSING!")
            
        # Check signals
        buy_signals = (df['Buy_Signal'] == 1).sum() if 'Buy_Signal' in df.columns else 0
        sell_signals = (df['Sell_Signal'] == 1).sum() if 'Sell_Signal' in df.columns else 0
        print(f"  Buy signals: {buy_signals}")
        print(f"  Sell signals: {sell_signals}")
    else:
        print("  NO DATA FIELD IN RESULTS!")
    
    print(f"\n6. Visualization result:")
    print(f"  Viz type: {type(viz)}")
    if isinstance(viz, dict):
        print(f"  Viz keys: {list(viz.keys())}")
        for key, value in viz.items():
            if isinstance(value, str):
                print(f"  {key}: {len(value)} characters")
            else:
                print(f"  {key}: {type(value)}")

if __name__ == "__main__":
    test_visualization_data()

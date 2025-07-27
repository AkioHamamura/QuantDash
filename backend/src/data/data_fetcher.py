# Yahoo Finance data fetcher
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import time
import sys
import os

# Fix import path when running from different directories
from src.utils.globals import DATA_PATH

def fetch_stock_data(ticker,
                     *, 
                     start_date=None, 
                     end_date=None, 
                     period=None, 
                     interval="1d",
                     save_to_parquet=False,
                     save_to_csv=False,
                     use_cache=True,
                     force_refresh=False
                     ) -> pd.DataFrame | None:
    """
    IMPLEMENT LATER: 
    - Multi-ticker support, e.g. fetch_stock_data(["NVDA", "AAPL"])
    - Caching only whole dataset, not individual dates, and retrieving by date range.

    Unified function to fetch stock data with intelligent caching.
    
    Args:
        ticker: str, stock ticker symbol (required)
        start_date: str, start date in 'YYYY-MM-DD' format (optional)
        end_date: str, end date in 'YYYY-MM-DD' format (optional)
        period: str, period string like '1d', '5d', '1mo', '1y', '5y', 'max' (optional)
        interval: str, interval string like '1m', '5m', '1h', '1d' (default: '1d')
        save_to_parquet: bool, save data to parquet format (default: False)
        save_to_csv: bool, save data to CSV format (default: False)
        use_cache: bool, whether to check for cached data first (default: True)
        force_refresh: bool, force fresh download even if cache exists (default: False)
    
    Returns:
        pandas DataFrame with OHLCV data or None if fetch fails.
        Columns include 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'.

    Usage Examples:
        fetch_stock_data("NVDA")                           # Max historical data (cached)
        fetch_stock_data("NVDA", period="5y")              # Last 5 years (cached)
        fetch_stock_data("NVDA", force_refresh=True)       # Force fresh download
        fetch_stock_data("NVDA", start_date="2020-01-01", end_date="2023-12-31") # Custom date range
    """
    import os
    
    # Generate cache filename based on parameters
    if period is None: period = "max"  # Default to max if period is not specified
    cache_params = f"{ticker}_{period}_{start_date}_{end_date}_{interval}"
    csv_cache_file = f"{DATA_PATH}/{cache_params}_data.csv"
    parquet_cache_file = f"{DATA_PATH}/{cache_params}_data.parquet"
    
    # Check for cached data first (if use_cache=True and not force_refresh)
    if use_cache and not force_refresh:
        # Check for parquet cache first (faster)
        if os.path.exists(parquet_cache_file):
            try:
                print(f"Loading {ticker} from parquet cache...")
                start_time = time.time()
                data = pd.read_parquet(parquet_cache_file)
                load_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                print(f"Loaded cached data: {data.shape[0]} rows in {load_time:.2f} ms")
                return data
            except Exception as e:
                print(f"Error loading parquet cache: {e}")
        
        # Check for CSV cache as fallback
        elif os.path.exists(csv_cache_file):
            try:
                print(f"Loading {ticker} from CSV cache...")
                start_time = time.time()
                data = pd.read_csv(csv_cache_file, index_col=0, parse_dates=True)
                load_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                print(f"Loaded cached data: {data.shape[0]} rows in {load_time:.2f} ms")
                return data
            except Exception as e:
                print(f"Error loading CSV cache: {e}")
    
    # No cache found or force_refresh=True, fetch fresh data
    print(f"Fetching fresh data for {ticker} from Yahoo Finance...")
    
    try:
        # Start timing the download
        download_start = time.time()
        
        if period is not None:
            # Use period-based download (overrides start/end dates)
            data = yf.download(ticker, period=period, interval=interval, auto_adjust=True)
        elif start_date is not None or end_date is not None:
            # Use date range download
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval, auto_adjust=True)
        else:
            # Default: fetch maximum available historical data
            data = yf.download(ticker, period="max", interval=interval, auto_adjust=True)
        
        download_time = (time.time() - download_start) * 1000  # Convert to milliseconds
        print(f"Data downloaded from Yahoo Finance: {data.shape[0]} rows in {download_time:.2f} ms") # type: ignore

        if data is not None and not data.empty:
            # Auto-save to cache (parquet preferred for performance)
            if use_cache:
                try:
                    data.to_parquet(parquet_cache_file)
                    print(f"Data cached to {parquet_cache_file}")
                except Exception as e:
                    print(f"Error saving parquet cache: {e}")
            
            # Save to parquet if explicitly requested
            if save_to_parquet:
                explicit_parquet = f"{DATA_PATH}/{ticker}_data.parquet"
                data.to_parquet(explicit_parquet)
                print(f"Data saved to {explicit_parquet}")

            # Save to CSV if explicitly requested
            if save_to_csv:
                explicit_csv = f"{DATA_PATH}/{ticker}_data.csv"
                data.to_csv(explicit_csv)
                print(f"Data saved to {explicit_csv}")

            return data
        else:
            print(f"No data found for {ticker} with the given parameters.")
            return None
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


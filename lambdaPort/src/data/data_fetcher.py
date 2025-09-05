# Yahoo Finance data fetcher
import pandas as pd
import matplotlib.pyplot as plt
import sys
import yfinance as yf
import time
import os

# Fix import path when running from different directories
from utils.globals import DATA_PATH

def write_available_tickers(cache_dir=DATA_PATH, interval="1d"):
    """
    Write available tickers (f"{ticker}_max_None_None_{interval}_data.parquet") to a text file for reference.
    This function is useful for debugging and ensuring the ticker list is up-to-date.
    """
    with open(f"{cache_dir}/available_tickers_{interval}.txt", "w") as f:
        for file in os.listdir(cache_dir):
            if file.endswith(f"max_None_None_{interval}_data.parquet"):
                ticker = file.split("_")[0]
                f.write(f"{ticker}\n")


def fetch_cached_data(ticker, period=None, start_date=None, end_date=None, interval="1d"):
    """
    Fetch cached data for a specific ticker and time range.

    works for both single index and multi-index dataframes.
    
    Note: yfinance DataFrames can have MultiIndex columns structure like:
    - Single ticker: Columns are ('Open', 'High', 'Low', 'Close', 'Volume')
    - Multiple tickers: Columns are MultiIndex like (('Open', 'AAPL'), ('Close', 'AAPL'))
    
    Since we cache max data and filter by period, we handle potential MultiIndex by flattening.
    """
    cache_file = f"{DATA_PATH}/{ticker}_max_None_None_{interval}_data.parquet"
    if not os.path.exists(cache_file):
        return None
        
    data_df = pd.read_parquet(cache_file)
    
    # Handle MultiIndex columns - flatten them for easier access (from viz.py pattern)
    if isinstance(data_df.columns, pd.MultiIndex):
        # Flatten MultiIndex columns by taking the first level that's not empty
        new_columns = []
        for col in data_df.columns:
            if isinstance(col, tuple):
                # Take the first non-empty part of the tuple
                new_col = col[0] if col[0] else col[1] if len(col) > 1 else str(col)
            else:
                new_col = col
            new_columns.append(new_col)
        data_df.columns = new_columns

    if period is None and start_date is None and end_date is None:
        # If no period or date range specified, return the entire cached data
        return data_df
    
    if period is not None:
        # If period is specified, filter the data from the last available date backwards
        last_date = data_df.index.max()  # Get the most recent date in the dataset
        
        if period == "1mo":
            return data_df[data_df.index >= last_date - pd.Timedelta(days=30)]
        elif period == "6mo":
            return data_df[data_df.index >= last_date - pd.Timedelta(days=180)]
        elif period == "1y":
            return data_df[data_df.index >= last_date - pd.Timedelta(days=365)]
        elif period == "2y":
            return data_df[data_df.index >= last_date - pd.Timedelta(days=2*365)]
        elif period == "3y":
            return data_df[data_df.index >= last_date - pd.Timedelta(days=3*365)]
        elif period == "4y":
            return data_df[data_df.index >= last_date - pd.Timedelta(days=4*365)]
        elif period == "5y":
            return data_df[data_df.index >= last_date - pd.Timedelta(days=5*365)]
        elif period == "max":
            return data_df
    
    # Handle start_date and end_date filtering if provided
    if start_date is not None or end_date is not None:
        if start_date:
            data_df = data_df[data_df.index >= pd.to_datetime(start_date)]
        if end_date:
            data_df = data_df[data_df.index <= pd.to_datetime(end_date)]
        return data_df
    
    return data_df



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
        print("Checking for cached data...")
        print(f"Looking for cache files at: {DATA_PATH}")
        print(f"Parquet cache file: {parquet_cache_file}")
        print(f"CSV cache file: {csv_cache_file}")
        
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
        else:
            print(f"No cache files found at expected locations")
    
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


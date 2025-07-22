# Yahoo Finance data fetcher
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

from utils.globals import DATA_PATH


def fetch_stock_data(ticker, 
                     *, 
                     start_date=None, 
                     end_date=None, 
                     period=None, 
                     interval="1d",
                     save_to_parquet=False,
                     save_to_csv=False
                     ) -> pd.DataFrame | None:
    """
    Unified function to fetch stock data with flexible parameters.
    
    Args:
        ticker: str, stock ticker symbol (required)
        start_date: str, start date in 'YYYY-MM-DD' format (optional)
        end_date: str, end date in 'YYYY-MM-DD' format (optional)
        period: str, period string like '1d', '5d', '1mo', '1y', '5y', 'max' (optional)
        interval: str, interval string like '1m', '5m', '1h', '1d' (default: '1d')
    
    Returns:
        pandas DataFrame with OHLCV data or None if fetch fails.
        Columns include 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'.

    Usage Examples:
        fetch_stock_data("NVDA")                           # Max historical data
        fetch_stock_data("NVDA", period="5y")              # Last 5 years
        fetch_stock_data("NVDA", period="1y", interval="1h") # Last year, hourly data
        fetch_stock_data("NVDA", "2020-01-01", "2023-12-31") # Custom date range
    """
    try:
        if period is not None:
            # Use period-based download (overrides start/end dates)
            data = yf.download(ticker, period=period, interval=interval, auto_adjust=True)
        elif start_date is not None or end_date is not None:
            # Use date range download
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval, auto_adjust=True)
        else:
            # Default: fetch maximum available historical data
            data = yf.download(ticker, period="max", interval=interval, auto_adjust=True)
        
        if data is not None:
            # Ensure data is not empty
            if data.empty:
                print(f"No data found for {ticker} with the given parameters.")
                return None
            
            # Save to parquet if requested
            if save_to_parquet:
                data.to_parquet(f"{DATA_PATH}/{ticker}_data.parquet")
                print(f"Data saved to {DATA_PATH}/{ticker}_data.parquet")

            # Save to CSV if requested
            if save_to_csv:
                data.to_csv(f"{DATA_PATH}/{ticker}_data.csv")
                print(f"Data saved to {DATA_PATH}/{ticker}_data.csv")

        return data
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


    
import sys
# Yahoo Finance data fetcher
import pandas as pd
import sys
import yfinance as yf
import time
import boto3

"""
Purpose of this lambda function:
- Simply call the yfinance library to fetch stock data then return it
- Needs a symbol as input parameter
- Example: POST Body: {"symbol": "NVDA"}
- Build with: docker buildx build --platform linux/amd64 --provenance=false -t docker-image:quantdash-datafetcher .
"""
def handler(event, context):
    if 'symbol' in event:
        symbol = event['symbol']
    else:
        symbol = "NVDA"
    data = fetch_stock_data(symbol)
    test(data)
    return {
        'statusCode': 200,
        'body': data.to_json()
    }

def test(data):
    #Just try to put the data as a csv to the s3 bucket
    s3_client = boto3.client('s3')
    # Define bucket and key
    bucket_name = 'quant-dash-cache'
    object_key = 'test.csv'

    # Content to upload
    file_content = data.to_csv()

    try:
        # Upload the object
        response = s3_client.put_object(
            Body=file_content,
            Bucket=bucket_name,
            Key=object_key
        )
        print(f"Object '{object_key}' uploaded successfully to bucket '{bucket_name}'.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error uploading object: {e}")

def fetch_stock_data(ticker="NVDA",
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
    if period is None: period = "max"  # Default to max if period is not specified

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

            return data
        else:
            print(f"No data found for {ticker} with the given parameters.")
            return None

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


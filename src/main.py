# Main entry point for QuantDash application
from data.data_fetcher import fetch_stock_data
import matplotlib.pyplot as plt

def main():
    #from src.dashboard.app import run_dash_app

    ## Run the Dash application
    #run_dash_app()
    tickers = [
        # Tech Giants
        "NVDA", "AAPL", "GOOGL", "AMZN", "MSFT", "META", "TSLA", "NFLX", "CRM", "ORCL",
    ]
    for ticker in tickers:
        fetch_stock_data(ticker)

if __name__ == "__main__":
    main()
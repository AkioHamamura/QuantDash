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
        
        # Financial Services
        "JPM", "BAC", "WFC", "GS", "MS", "C", "V", "MA", "AXP", "BLK",
        
        # Healthcare & Pharma
        "JNJ", "PFE", "UNH", "ABBV", "TMO", "ABT", "BMY", "MRK", "LLY", "CVS",
        
        # Consumer & Retail
        "WMT", "HD", "PG", "KO", "PEP", "NKE", "SBUX", "MCD", "DIS", "COST",
        
        # Industrial & Energy
        "XOM", "CVX", "GE", "CAT", "BA", "MMM", "HON", "UPS", "RTX", "LMT",
        
        # Communication & Media
        "VZ", "T", "CMCSA", "TMUS", "CHTR", "PARA", "WBD", "NFLX", "SPOT", "ROKU",
        
        # ETFs for Market Tracking
        "SPY", "QQQ", "IWM", "VTI", "VOO", "ARKK", "XLF", "XLK", "XLE", "XLV"
    ]
    for ticker in tickers:
        fetch_stock_data(ticker)




if __name__ == "__main__":    
    main()
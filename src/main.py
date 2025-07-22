# Main entry point for QuantDash application
from data.data_fetcher import fetch_stock_data

def main():
    #from src.dashboard.app import run_dash_app

    ## Run the Dash application
    #run_dash_app()
    data = fetch_stock_data("AAPL", start_date="2020-01-01", end_date="2025-01-01")
    print(data.head()) # type: ignore













if __name__ == "__main__":    
    main()
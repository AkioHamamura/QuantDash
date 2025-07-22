# Main entry point for QuantDash application
from data.data_fetcher import fetch_stock_data
import matplotlib.pyplot as plt

def main():
    #from src.dashboard.app import run_dash_app

    ## Run the Dash application
    #run_dash_app()
    data = fetch_stock_data("KBGGY")
    if data is not None:
        plt.plot(data.index, data['Close'])
        plt.title("KBGGY Stock Price")
        plt.xlabel("Date")
        plt.ylabel("Close Price")
        plt.show()







if __name__ == "__main__":    
    main()
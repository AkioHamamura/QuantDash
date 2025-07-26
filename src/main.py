# Main entry point for QuantDash application
from backtesting.engine import BacktestEngine
from strategies.ma_crossover import MovingAverageCrossover
from data.data_fetcher import fetch_stock_data
from backtesting.viz import visualize_results

def main():
    #from src.dashboard.app import run_dash_app

    ## Run the Dash application
    #run_dash_app()

    #fetch_stock_data("CARV", save_to_csv=True)
    data = fetch_stock_data("AMZN", period="6y")
    if data is None or data.empty:
        print("Failed to fetch data")
        return
    strategy = MovingAverageCrossover(fast_period=10, slow_period=30)
    engine = BacktestEngine(strategy)
    engine.run(data)






if __name__ == "__main__":
    main()
# Main entry point for QuantDash application
from src.backtesting.engine import BacktestEngine
from src.strategies.ma_crossover import MovingAverageCrossover
from src.data.data_fetcher import fetch_stock_data
from src.backtesting.viz import visualize_results

def main():
    #from src.dashboard.app import run_dash_app

    ## Run the Dash application
    #run_dash_app()

    #fetch_stock_data("CARV", save_to_csv=True)
    data = fetch_stock_data("AAPL", period="1y")
    if data is None or data.empty:
        print("Failed to fetch data")
        return
    strategy = MovingAverageCrossover(fast_period=12, slow_period=26, initial_cash=1000)
    engine = BacktestEngine(strategy)
    engine.run(data)






if __name__ == "__main__":
    main()
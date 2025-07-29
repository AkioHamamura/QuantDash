# Main entry point for QuantDash application
from src.backtesting.engine import BacktestEngine
from src.strategies.ma_crossover import MovingAverageCrossover
from src.data.data_fetcher import fetch_stock_data
from src.backtesting.viz import visualize_results
from src.utils.globals import DATA_PATH
from src.data.data_fetcher import write_available_tickers




if __name__ == "__main__":
    write_available_tickers()
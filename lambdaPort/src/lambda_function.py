#from src.backtesting.engine import BacktestEngine
#from src.strategies.ma_crossover import MovingAverageCrossover
#from src.data.data_fetcher import fetch_stock_data
#from src.backtesting.viz import visualize_results
#from src.utils.globals import DATA_PATH
#from src.api.server import *
#from lambdaPort.src.api.server import *
from api.server import root
"""
Main entry point for the Quantdash Lambda function
"""
def handler(event, context):
    if 'route' not in event:
        return {
            'statusCode': 400,
            'body': "Missing 'route' parameter in request body"
        }
    #Forwards the event body to the proper function
    #Example, if route = '/', execute async def root from src.api/servery.py

    if 'route' == '/':
        return root()

   # if 'route' == '/health':
   #     return health_check()
#
   # if 'route' == '/api/tickers':
   #     return get_available_tickers()
#
   # if 'route' == '/api/strategies':
   #     return get_available_strategies()
#
   # if 'route' == 'api/backtest':
   #     return run_backtest(event)

    else:
        return {
            'statusCode': 404,
            'body': "Route not found"
        }


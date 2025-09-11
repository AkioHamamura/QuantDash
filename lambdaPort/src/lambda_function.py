from .api.server import *
from .lambdaFunctionsTester import *

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
    print(event)
    if event['route'] == '/':
        return root()

    if event['route'] == '/test':
        return run_tests()

    if event['route'] == '/api/tickers':
        return get_available_tickers()

    if event['route'] == '/api/strategies':
        return get_available_strategies()

    if event['route'] == '/api/backtest':
        return run_backtest(event)

    else:
        return {
            'statusCode': 404,
            'body': "Route not found"
        }


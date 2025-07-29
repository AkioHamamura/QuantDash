from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import pandas as pd
import sys
import os
import numpy as np
from datetime import datetime, date

# Add the backend/src directory to Python path for imports
backend_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_src_path not in sys.path:
    sys.path.insert(0, backend_src_path)

# Also add the backend directory to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

print(f"Python path includes: {backend_src_path}")
print(f"Python path includes: {backend_path}")

from backtesting.engine import BacktestEngine
from strategies.ma_crossover import MovingAverageCrossover
from strategies.bollinger_breakout import BollingerBreakout
from strategies.dual_momentum import DualMomentum
from strategies.gap_fade import GapFade
from strategies.rsi_pullback import RSIPullback
from strategies.turtle_breakout import TurtleBreakout
from strategies.pair_trading import PairTrading
from data.data_fetcher import fetch_stock_data, fetch_cached_data
from utils.helpers import make_json_serializable
from utils.globals import DATA_PATH


app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BacktestRequest(BaseModel):
    symbol: str  # Changed from 'ticker' to match frontend
    period: str = "1y"
    algorithm: str = "moving_average_crossover"
    initial_cash: Optional[int] = 10000
    algorithm_specific_params: Optional[Dict] = {}

@app.get("/api/tickers")
async def get_available_tickers():
    """Get list of available stock tickers from cache"""
    try:
        tickers_file = os.path.join(DATA_PATH, "available_tickers_1d.txt")
        if os.path.exists(tickers_file):
            with open(tickers_file, 'r') as f:
                tickers = [line.strip() for line in f.readlines() if line.strip()]
            return {"success": True, "tickers": sorted(tickers)}
        else:
            return {"success": False, "error": "Tickers file not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/strategies")
async def get_available_strategies():
    """Get list of available trading strategies with their parameters"""
    strategies = {
        "moving_average_crossover": {
            "name": "Moving Average Crossover",
            "description": "Buy when fast MA crosses above slow MA, sell when it crosses below",
            "parameters": {
                "fast_period": {"type": "number", "default": 12, "min": 5, "max": 50, "description": "Fast moving average period"},
                "slow_period": {"type": "number", "default": 26, "min": 10, "max": 100, "description": "Slow moving average period"}
            }
        },
        "bollinger_breakout": {
            "name": "Bollinger Band Breakout",
            "description": "Buy when price breaks above upper band, sell when it breaks below lower band",
            "parameters": {
                "period": {"type": "number", "default": 20, "min": 10, "max": 50, "description": "Bollinger Band period"},
                "std_dev": {"type": "number", "default": 2.0, "min": 1.0, "max": 3.0, "step": 0.1, "description": "Standard deviation multiplier"}
            }
        },
        "dual_momentum": {
            "name": "Dual Momentum",
            "description": "Trade based on relative and absolute momentum signals",
            "parameters": {
                "lookback_period": {"type": "number", "default": 60, "min": 20, "max": 120, "description": "Momentum calculation period"},
                "risk_free_rate": {"type": "number", "default": 0.02, "min": 0.0, "max": 0.1, "step": 0.01, "description": "Annual risk-free rate"}
            }
        },
        "gap_fade": {
            "name": "Gap Fade",
            "description": "Fade significant price gaps expecting mean reversion",
            "parameters": {
                "gap_threshold": {"type": "number", "default": 0.02, "min": 0.01, "max": 0.05, "step": 0.01, "description": "Minimum gap size (%)"},
                "stop_loss": {"type": "number", "default": 0.05, "min": 0.02, "max": 0.1, "step": 0.01, "description": "Stop loss percentage"}
            }
        },
        "rsi_pullback": {
            "name": "RSI Pullback",
            "description": "Buy oversold pullbacks in uptrends, sell overbought rallies in downtrends",
            "parameters": {
                "rsi_period": {"type": "number", "default": 14, "min": 7, "max": 30, "description": "RSI calculation period"},
                "ma_period": {"type": "number", "default": 50, "min": 20, "max": 100, "description": "Trend MA period"},
                "oversold": {"type": "number", "default": 30, "min": 20, "max": 40, "description": "RSI oversold threshold"},
                "overbought": {"type": "number", "default": 70, "min": 60, "max": 80, "description": "RSI overbought threshold"}
            }
        },
        "turtle_breakout": {
            "name": "Turtle Breakout",
            "description": "Trade channel breakouts with ATR-based position sizing",
            "parameters": {
                "entry_period": {"type": "number", "default": 20, "min": 10, "max": 50, "description": "Entry breakout period"},
                "exit_period": {"type": "number", "default": 10, "min": 5, "max": 30, "description": "Exit breakout period"},
                "atr_period": {"type": "number", "default": 20, "min": 10, "max": 30, "description": "ATR calculation period"},
                "risk_percent": {"type": "number", "default": 0.02, "min": 0.01, "max": 0.05, "step": 0.01, "description": "Risk per trade (%)"}
            }
        },
        "pair_trading": {
            "name": "Pair Trading",
            "description": "Statistical arbitrage based on Z-score mean reversion",
            "parameters": {
                "lookback_period": {"type": "number", "default": 60, "min": 30, "max": 120, "description": "Lookback period for statistics"},
                "entry_threshold": {"type": "number", "default": 2.0, "min": 1.5, "max": 3.0, "step": 0.1, "description": "Z-score entry threshold"},
                "exit_threshold": {"type": "number", "default": 0.5, "min": 0.1, "max": 1.0, "step": 0.1, "description": "Z-score exit threshold"}
            }
        }
    }
    
    return {"success": True, "strategies": strategies}

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    if request.method == "POST":
        # Try to read the body for debugging
        try:
            body = await request.body()
            print(f"Request body: {body.decode()}")
        except Exception as e:
            print(f"Could not read body: {e}")
    
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response


@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    try:
        print(f"Received request: {request}")
        
        # Fetch data using your existing function
        print(f"Fetching cached data for {request.symbol}, period: {request.period}")
        data = fetch_cached_data(request.symbol, period=request.period)
        
        # Debug data fetching
        print(f"Data result: {type(data)}")
        if data is not None:
            print(f"Data shape: {data.shape}")
            print(f"Data columns: {list(data.columns)}")
            print(f"Data index type: {type(data.index)}")
            print(f"Data not empty: {not data.empty}")
        else:
            print("Data is None")
            
        if data is None or data.empty:
            print("Failed to fetch data - returning error")
            return {"success": False, "error": "Failed to fetch data"}
        
        # Get algorithm parameters (support both old and new parameter names)
        params = request.algorithm_specific_params or {}
        print(f"Algorithm params: {params}")
        
        # Initialize strategy based on algorithm type
        initial_cash = request.initial_cash or 10000
        
        if request.algorithm == "moving_average_crossover":
            strategy = MovingAverageCrossover(
                fast_period=params.get("fast_period", 12),
                slow_period=params.get("slow_period", 26),
                initial_cash=initial_cash
            )
        elif request.algorithm == "bollinger_breakout":
            strategy = BollingerBreakout(
                period=params.get("period", 20),
                std_dev=params.get("std_dev", 2.0),
                initial_cash=initial_cash
            )
        elif request.algorithm == "dual_momentum":
            strategy = DualMomentum(
                lookback_period=params.get("lookback_period", 60),
                risk_free_rate=params.get("risk_free_rate", 0.02),
                initial_cash=initial_cash
            )
        elif request.algorithm == "gap_fade":
            strategy = GapFade(
                gap_threshold=params.get("gap_threshold", 0.02),
                stop_loss=params.get("stop_loss", 0.05),
                initial_cash=initial_cash
            )
        elif request.algorithm == "rsi_pullback":
            strategy = RSIPullback(
                rsi_period=params.get("rsi_period", 14),
                ma_period=params.get("ma_period", 50),
                oversold=params.get("oversold", 30),
                overbought=params.get("overbought", 70),
                initial_cash=initial_cash
            )
        elif request.algorithm == "turtle_breakout":
            strategy = TurtleBreakout(
                entry_period=params.get("entry_period", 20),
                exit_period=params.get("exit_period", 10),
                atr_period=params.get("atr_period", 20),
                risk_percent=params.get("risk_percent", 0.02),
                initial_cash=initial_cash
            )
        elif request.algorithm == "pair_trading":
            strategy = PairTrading(
                lookback_period=params.get("lookback_period", 60),
                entry_threshold=params.get("entry_threshold", 2.0),
                exit_threshold=params.get("exit_threshold", 0.5),
                initial_cash=initial_cash
            )
        else:
            # Default to moving average crossover
            strategy = MovingAverageCrossover(
                fast_period=params.get("fast_period", 12),
                slow_period=params.get("slow_period", 26),
                initial_cash=initial_cash
            )
        
        print(f"Strategy initialized: {strategy}")
        print(f"Strategy name: {strategy.name}")
        
        # Run backtest
        engine = BacktestEngine(strategy)
        print("Running backtest...")
        results, viz = engine.run(data, visualize=True)
        


        print(f"Raw results type: {type(results)}")
        print(f"Raw results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
        
        # Remove problematic fields that aren't needed for frontend
        if isinstance(results, dict):
            # Remove the 'data' field as it likely contains the original DataFrame
            results_copy = results.copy()
            if 'data' in results_copy:
                print(f"Removing 'data' field of type: {type(results_copy['data'])}")
                del results_copy['data']
            results = results_copy
        
        # Convert results to JSON-serializable format
        serializable_results = make_json_serializable(results)
        
        # Map your backend field names to frontend expected names
        if isinstance(serializable_results, dict):
            frontend_results = {
                "strategy": serializable_results.get("strategy", "Moving Average Crossover"),
                "parameters": serializable_results.get("parameters", {}),
                "total_return": serializable_results.get("total_return_pct", 0),
                "final_value": serializable_results.get("final_value", 0),
                "sharpe_ratio": serializable_results.get("sharpe_ratio", 0),
                "sortino_ratio": serializable_results.get("sortino_ratio", 0),
                "max_drawdown": serializable_results.get("max_drawdown_pct", 0),
                "volatility_pct": serializable_results.get("volatility_pct", 0),
                "win_rate": serializable_results.get("win_rate_pct", 0),
                "total_trades": serializable_results.get("total_trades", 0),
                "portfolio_values": serializable_results.get("portfolio_values", []),
                "trades": serializable_results.get("trades", [])
            }
        else:
            # Fallback if serialization didn't return a dict
            frontend_results = {
                "strategy": "Moving Average Crossover",
                "parameters": {},
                "total_return": 0,
                "final_value": 0,
                "sharpe_ratio": 0,
                "sortino_ratio": 0,
                "max_drawdown": 0,
                "volatility_pct": 0,
                "win_rate": 0,
                "total_trades": 0,
                "portfolio_values": [],
                "trades": []
            }

        return {
            "success": True, 
            "data": frontend_results, 
            "visualizations": viz  # Include the visualization data from get_json_visualizations()
        }

    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}"
        print(f"Exception occurred: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": error_msg}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
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
from data.data_fetcher import fetch_stock_data
from utils.helpers import make_json_serializable


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
    symbol: str
    period: str = "1y"
    algorithm: str = "moving_average_crossover"
    initial_cash: Optional[int] = 10000
    algorithm_specific_params: Optional[Dict] = {}

@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    try:
        print(f"Received request: {request}")
        
        # Fetch data using your existing function
        data = fetch_stock_data(request.symbol, period=request.period, use_cache=True)
        if data is None or data.empty:
            return {"success": False, "error": "Failed to fetch data"}
        
        # Get algorithm parameters (support both old and new parameter names)
        params = request.algorithm_specific_params or {}
        
        # Initialize your strategy
        strategy = MovingAverageCrossover(
            fast_period=params.get("fast_period", 12),
            slow_period=params.get("slow_period", 26),
            initial_cash=request.initial_cash or 10000
        )
        
        # Run backtest
        engine = BacktestEngine(strategy)
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
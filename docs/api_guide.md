# QuantDash API Guide

A comprehensive guide to understanding how data flows between your React frontend and Python backend for algorithmic trading backtests.

## 🎯 Overview: The Complete API Flow

```
Frontend Form Input → HTTP Request → Python Backend → Backtesting → Results + Charts → Frontend Display
```

### **The Journey of a Backtest Request:**

1. **User Input** (Frontend) → User enters stock symbol, period, strategy parameters
2. **API Call** (Frontend) → React sends HTTP POST request to Python backend
3. **Data Processing** (Backend) → Python fetches stock data and runs backtest
4. **Results Generation** (Backend) → Creates performance metrics and Plotly charts
5. **Response** (Backend → Frontend) → Sends JSON with results and chart data
6. **Display** (Frontend) → React updates UI with charts and metrics

---

## 📋 Step-by-Step API Process

### **Step 1: Frontend User Input**

**File:** `frontend/src/pages/Index.tsx`

```tsx
// User inputs captured by React state
const [symbol, setSymbol] = useState('AAPL');
const [period, setPeriod] = useState('1y');
const [fastPeriod, setFastPeriod] = useState(12);
const [slowPeriod, setSlowPeriod] = useState(26);
const [initialCash, setInitialCash] = useState(10000);

// Form submission handler
const handleSubmit = async (e) => {
  e.preventDefault();
  
  // Prepare request data
  const request = {
    symbol: symbol,           // "AAPL"
    period: period,          // "1y"
    strategy_params: {
      fast_period: fastPeriod,    // 12
      slow_period: slowPeriod,    // 26
      initial_cash: initialCash   // 10000
    }
  };

  // Send to backend
  const result = await apiClient.runBacktest(request);
  
  // Handle response
  if (result.success) {
    setChartData(result.data);  // Update UI with results
  } else {
    console.error('Error:', result.error);
  }
};
```

### **Step 2: API Client (HTTP Communication)**

**File:** `frontend/src/services/api.ts`

```typescript
export const apiClient = {
  async runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
    try {
      // HTTP POST request to Python backend
      const response = await fetch('http://localhost:8000/api/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),  // Convert to JSON string
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();  // Parse JSON response
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }
};
```

### **Step 3: Backend API Endpoint (FastAPI Server)**

**File:** `backend/src/api/server.py` (to be created)

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import your existing backend components
from src.backtesting.engine import BacktestEngine
from src.strategies.ma_crossover import MovingAverageCrossover
from src.data.data_fetcher import fetch_stock_data

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class BacktestRequest(BaseModel):
    symbol: str
    period: str = "1y"
    strategy_params: Dict = {}

class BacktestResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None

@app.post("/api/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    Main backtest endpoint - receives user parameters and returns results + charts
    """
    try:
        # Step 1: Fetch stock data
        print(f"Fetching data for {request.symbol}, period: {request.period}")
        data = fetch_stock_data(
            request.symbol, 
            period=request.period,
            use_cache=True
        )
        
        if data is None or data.empty:
            return BacktestResponse(
                success=False, 
                error=f"Failed to fetch data for {request.symbol}"
            )
        
        # Step 2: Initialize strategy with user parameters
        strategy = MovingAverageCrossover(
            fast_period=request.strategy_params.get("fast_period", 12),
            slow_period=request.strategy_params.get("slow_period", 26),
            initial_cash=request.strategy_params.get("initial_cash", 10000)
        )
        
        # Step 3: Run backtest
        print("Running backtest...")
        engine = BacktestEngine(strategy)
        results = engine.run(data, visualize=False)  # Don't show plots on server
        
        # Step 4: Create charts for frontend
        chart_data = create_plotly_charts(results)
        
        # Step 5: Prepare response
        response_data = {
            "metrics": results.get("metrics", {}),
            "charts": chart_data,
            "summary": {
                "symbol": request.symbol,
                "period": request.period,
                "strategy": "Moving Average Crossover",
                "parameters": request.strategy_params
            }
        }
        
        return BacktestResponse(success=True, data=response_data)
    
    except Exception as e:
        print(f"Error in backtest: {str(e)}")
        return BacktestResponse(success=False, error=str(e))

def create_plotly_charts(results: Dict) -> Dict:
    """
    Convert backtest results into Plotly chart data for frontend display
    """
    data = results['data']
    
    # Create price chart with moving averages and signals
    price_chart = {
        "data": [
            {
                "x": data.index.tolist(),
                "y": data['Close'].tolist(),
                "type": "scatter",
                "mode": "lines",
                "name": "Price",
                "line": {"color": "#2563eb"}
            },
            {
                "x": data.index.tolist(),
                "y": data['MA_Fast'].tolist(),
                "type": "scatter",
                "mode": "lines",
                "name": f"MA Fast",
                "line": {"color": "#dc2626"}
            },
            {
                "x": data.index.tolist(),
                "y": data['MA_Slow'].tolist(),
                "type": "scatter",
                "mode": "lines",
                "name": f"MA Slow",
                "line": {"color": "#16a34a"}
            }
        ],
        "layout": {
            "title": "Stock Price & Moving Averages",
            "xaxis": {"title": "Date"},
            "yaxis": {"title": "Price ($)"},
            "height": 400
        }
    }
    
    # Create portfolio performance chart
    performance_chart = {
        "data": [
            {
                "x": data.index.tolist(),
                "y": data['Portfolio_Value'].tolist(),
                "type": "scatter",
                "mode": "lines",
                "name": "Strategy",
                "line": {"color": "#7c3aed"}
            },
            {
                "x": data.index.tolist(),
                "y": data['Benchmark_Value'].tolist() if 'Benchmark_Value' in data.columns else data['Close'].tolist(),
                "type": "scatter",
                "mode": "lines",
                "name": "Buy & Hold",
                "line": {"color": "#059669"}
            }
        ],
        "layout": {
            "title": "Portfolio Performance",
            "xaxis": {"title": "Date"},
            "yaxis": {"title": "Portfolio Value ($)"},
            "height": 400
        }
    }
    
    return {
        "price_chart": price_chart,
        "performance_chart": performance_chart
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### **Step 4: Backend Processing (Your Existing Components)**

#### **A. Data Fetching**
```python
# src/data/data_fetcher.py (your existing code)
data = fetch_stock_data("AAPL", period="1y", use_cache=True)
# Returns: pandas DataFrame with OHLCV data
```

#### **B. Strategy Execution**
```python
# src/strategies/ma_crossover.py (your existing code)
strategy = MovingAverageCrossover(fast_period=12, slow_period=26, initial_cash=10000)
# Processes data and generates buy/sell signals
```

#### **C. Backtesting Engine**
```python
# src/backtesting/engine.py (your existing code)
engine = BacktestEngine(strategy)
results = engine.run(data, visualize=False)
# Returns: Dict with data, metrics, and performance stats
```

### **Step 5: Response Back to Frontend**

#### **A. JSON Response Structure**
```json
{
  "success": true,
  "data": {
    "metrics": {
      "total_return": 0.152,
      "sharpe_ratio": 1.23,
      "max_drawdown": -0.084,
      "win_rate": 0.58,
      "profit_factor": 1.34
    },
    "charts": {
      "price_chart": {
        "data": [...],
        "layout": {...}
      },
      "performance_chart": {
        "data": [...],
        "layout": {...}
      }
    },
    "summary": {
      "symbol": "AAPL",
      "period": "1y",
      "strategy": "Moving Average Crossover",
      "parameters": {
        "fast_period": 12,
        "slow_period": 26,
        "initial_cash": 10000
      }
    }
  }
}
```

### **Step 6: Frontend Chart Display**

**File:** `frontend/src/components/PlotlyChart.tsx`

```tsx
import Plot from 'react-plotly.js';

export const PriceChart = ({ chartData }) => {
  return (
    <Plot
      data={chartData.price_chart.data}
      layout={chartData.price_chart.layout}
      style={{ width: '100%' }}
    />
  );
};

export const PerformanceChart = ({ chartData }) => {
  return (
    <Plot
      data={chartData.performance_chart.data}
      layout={chartData.performance_chart.layout}
      style={{ width: '100%' }}
    />
  );
};
```

---

## 🔄 Data Flow Summary

### **Request Flow:**
```
User Form → React State → JSON Request → FastAPI → Python Functions → Database/Cache
```

### **Response Flow:**
```
Backtest Results → Plotly Charts → JSON Response → React State → Chart Components → User Display
```

### **Data Transformations:**

1. **Frontend Input:**
   ```javascript
   { symbol: "AAPL", period: "1y", strategy_params: { fast_period: 12 } }
   ```

2. **Backend Processing:**
   ```python
   data = fetch_stock_data("AAPL", period="1y")  # pandas DataFrame
   results = engine.run(data)                     # Dict with metrics
   ```

3. **Chart Serialization:**
   ```python
   chart_data = {
     "data": [{"x": dates, "y": prices, "type": "scatter"}],
     "layout": {"title": "Price Chart"}
   }
   ```

4. **Frontend Display:**
   ```tsx
   <Plot data={chartData.data} layout={chartData.layout} />
   ```

---

## 🚀 Quick Setup Guide

### **1. Start Backend Server:**
```bash
conda activate quant
cd backend
python src/api/server.py
# Server starts at: http://localhost:8000
```

### **2. Start Frontend:**
```bash
conda activate quant
cd frontend
npm run dev
# Frontend starts at: http://localhost:5173
```

### **3. Test API Connection:**
```bash
# Test endpoint directly
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "period": "1y", "strategy_params": {"fast_period": 12}}'
```

---

## 🔧 API Endpoints

### **POST /api/backtest**
- **Purpose:** Run backtest with user parameters
- **Input:** BacktestRequest (symbol, period, strategy_params)
- **Output:** BacktestResponse (success, data/charts, error)

### **GET /api/stocks/{symbol}/data**
- **Purpose:** Get raw stock data (optional endpoint)
- **Input:** symbol (path), period (query)
- **Output:** JSON with OHLCV data

---

## 🐛 Error Handling

### **Common Errors:**

1. **CORS Issues:**
   ```
   Error: Access to fetch blocked by CORS policy
   Solution: Ensure CORS middleware is configured in FastAPI
   ```

2. **Data Not Found:**
   ```
   Error: Failed to fetch data for INVALID_SYMBOL
   Solution: Validate symbol before processing
   ```

3. **Serialization Errors:**
   ```
   Error: Object of type 'Timestamp' is not JSON serializable
   Solution: Convert pandas objects to Python primitives
   ```

---

## 📊 Chart Data Format

### **Plotly Chart Structure:**
```javascript
{
  "data": [
    {
      "x": ["2023-01-01", "2023-01-02", ...],  // Dates
      "y": [150.25, 151.30, ...],              // Values
      "type": "scatter",
      "mode": "lines",
      "name": "Price",
      "line": {"color": "#2563eb"}
    }
  ],
  "layout": {
    "title": "Stock Price Chart",
    "xaxis": {"title": "Date"},
    "yaxis": {"title": "Price ($)"},
    "height": 400,
    "showlegend": true
  }
}
```

This format allows React-Plotly.js to render interactive charts directly in your frontend!

---

## 🎯 Next Steps

1. **Create the FastAPI server** using the code above
2. **Test the API connection** between frontend and backend
3. **Add Plotly charts** to your React components
4. **Handle loading states** and errors in the frontend
5. **Extend with more strategy parameters** and chart types

The API design is simple but powerful - it separates concerns cleanly while providing rich interactive visualizations for your trading dashboard! 🚀

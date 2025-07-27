# QuantDash Frontend

A simplified React-based frontend for the QuantDash algorithmic trading and backtesting platform.

## Quick Start

```bash
# Activate conda environment
conda activate quant

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Technology Stack

- **React 18** with TypeScript - Simplified, no complex routing
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Basic UI components** - Only essential ones kept
- **Simple API client** for backend communication

## Working with This Frontend

This guide shows you how to work with the simplified frontend and connect it to your Python backend.

### 1. Connecting to Your Python Backend

#### Step 1: Create a FastAPI Server

Create `src/api/server.py` in your main QuantDash directory:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import pandas as pd
from backtesting.engine import BacktestEngine
from strategies.ma_crossover import MovingAverageCrossover
from data.data_fetcher import fetch_stock_data

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
    strategy_params: Dict = {}

@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    try:
        # Fetch data using your existing function
        data = fetch_stock_data(request.symbol, period=request.period)
        if data is None or data.empty:
            return {"success": False, "error": "Failed to fetch data"}
        
        # Initialize your strategy
        strategy = MovingAverageCrossover(
            fast_period=request.strategy_params.get("fast_period", 12),
            slow_period=request.strategy_params.get("slow_period", 26),
            initial_cash=request.strategy_params.get("initial_cash", 10000)
        )
        
        # Run backtest
        engine = BacktestEngine(strategy)
        results = engine.run(data, visualize=False)
        
        return {"success": True, "data": results}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Step 2: Start Your Backend

```bash
conda activate quant
cd /path/to/QuantDash
python src/api/server.py
```

#### Step 3: Update Frontend API Calls

The API client is already set up in `src/services/api.ts`. To connect to your backend, just make sure the URLs match:

```typescript
// In src/services/api.ts - this is already configured
const API_BASE_URL = 'http://localhost:8000/api';
```

### 2. How to Change How It Looks

#### Using Tailwind CSS Classes

The frontend uses Tailwind CSS. You can modify styles by changing class names in `src/pages/Index.tsx`:

```tsx
// Current styling
<div className="min-h-screen bg-gray-50 p-8">

// Change to dark theme
<div className="min-h-screen bg-gray-900 p-8">

// Change card colors
<div className="bg-white p-6 rounded-lg shadow">  // Light card
<div className="bg-gray-800 p-6 rounded-lg shadow text-white">  // Dark card
```

#### Customize CSS

You can also add custom styles in `src/App.css`:

```css
/* Add custom styles */
.trading-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.results-positive {
  color: #10b981;  /* Green */
}

.results-negative {
  color: #ef4444;  /* Red */
}
```

Then use them in your components:
```tsx
<div className="trading-card p-6 rounded-lg">
  <span className="results-positive">+15.2%</span>
</div>
```

### 3. How to Add New Input Fields

#### Adding Date Inputs

Modify `src/pages/Index.tsx` to add start/end date inputs:

```tsx
// Add to the component state (inside the Index function)
const [startDate, setStartDate] = useState('2023-01-01');
const [endDate, setEndDate] = useState('2024-01-01');

// Add to the form HTML
<div>
  <label className="block text-sm font-medium text-gray-700">
    Start Date
  </label>
  <input
    type="date"
    value={startDate}
    onChange={(e) => setStartDate(e.target.value)}
    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
  />
</div>

<div>
  <label className="block text-sm font-medium text-gray-700">
    End Date
  </label>
  <input
    type="date"
    value={endDate}
    onChange={(e) => setEndDate(e.target.value)}
    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
  />
</div>
```

#### Adding Strategy Parameters

```tsx
// Add more strategy inputs
const [rsiPeriod, setRsiPeriod] = useState(14);
const [stopLoss, setStopLoss] = useState(5);

// Add to form
<div>
  <label className="block text-sm font-medium text-gray-700">
    RSI Period
  </label>
  <input
    type="number"
    value={rsiPeriod}
    onChange={(e) => setRsiPeriod(Number(e.target.value))}
    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
  />
</div>

<div>
  <label className="block text-sm font-medium text-gray-700">
    Stop Loss %
  </label>
  <input
    type="number"
    value={stopLoss}
    onChange={(e) => setStopLoss(Number(e.target.value))}
    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
  />
</div>
```

#### Making the Form Work

Update the form submission to send new parameters:

```tsx
const handleSubmit = async (e) => {
  e.preventDefault();
  
  const request = {
    symbol,
    period,
    start_date: startDate,
    end_date: endDate,
    strategy_params: {
      fast_period: fastPeriod,
      slow_period: slowPeriod,
      rsi_period: rsiPeriod,
      stop_loss: stopLoss,
      initial_cash: initialCash,
    },
  };

  try {
    const result = await apiClient.runBacktest(request);
    console.log('Backtest result:', result);
    // Update your UI with results
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### 4. How to Add Plotly Charts

#### Step 1: Install Plotly

```bash
conda activate quant
cd frontend
npm install react-plotly.js plotly.js
npm install --save-dev @types/plotly.js
```

#### Step 2: Create a Chart Component

Create `src/components/PlotlyChart.tsx`:

```tsx
import React from 'react';
import Plot from 'react-plotly.js';

interface ChartProps {
  data: any[];
  title?: string;
}

export const PriceChart: React.FC<ChartProps> = ({ data, title = 'Stock Price' }) => {
  // Transform your data for Plotly
  const dates = data.map(d => d.date);
  const prices = data.map(d => d.close);
  const ma_fast = data.map(d => d.ma_fast);
  const ma_slow = data.map(d => d.ma_slow);

  const plotData = [
    {
      x: dates,
      y: prices,
      type: 'scatter',
      mode: 'lines',
      name: 'Price',
      line: { color: '#2563eb' },
    },
    {
      x: dates,
      y: ma_fast,
      type: 'scatter',
      mode: 'lines',
      name: 'Fast MA',
      line: { color: '#dc2626' },
    },
    {
      x: dates,
      y: ma_slow,
      type: 'scatter',
      mode: 'lines',
      name: 'Slow MA',
      line: { color: '#16a34a' },
    },
  ];

  const layout = {
    title: title,
    xaxis: { title: 'Date' },
    yaxis: { title: 'Price ($)' },
    height: 400,
    showlegend: true,
  };

  return <Plot data={plotData} layout={layout} style={{ width: '100%' }} />;
};

export const PerformanceChart: React.FC<ChartProps> = ({ data, title = 'Portfolio Performance' }) => {
  const dates = data.map(d => d.date);
  const portfolioValues = data.map(d => d.portfolio_value);
  const benchmark = data.map(d => d.benchmark_value || d.close);

  const plotData = [
    {
      x: dates,
      y: portfolioValues,
      type: 'scatter',
      mode: 'lines',
      name: 'Strategy',
      line: { color: '#7c3aed' },
    },
    {
      x: dates,
      y: benchmark,
      type: 'scatter',
      mode: 'lines',
      name: 'Buy & Hold',
      line: { color: '#059669' },
    },
  ];

  const layout = {
    title: title,
    xaxis: { title: 'Date' },
    yaxis: { title: 'Portfolio Value ($)' },
    height: 400,
    showlegend: true,
  };

  return <Plot data={plotData} layout={layout} style={{ width: '100%' }} />;
};
```

#### Step 3: Use Charts in Your Main Page

Update `src/pages/Index.tsx`:

```tsx
import { PriceChart, PerformanceChart } from '../components/PlotlyChart';

// Inside your component, after getting results
const [chartData, setChartData] = useState(null);

const handleSubmit = async (e) => {
  e.preventDefault();
  // ... your existing code ...
  
  if (result.success) {
    setChartData(result.data);
  }
};

// In your JSX, replace the chart placeholder:
{chartData ? (
  <div className="col-span-full bg-white p-6 rounded-lg shadow">
    <PriceChart data={chartData.price_data} title="Price & Moving Averages" />
    <PerformanceChart data={chartData.portfolio_data} title="Strategy Performance" />
  </div>
) : (
  <div className="bg-white p-6 rounded-lg shadow">
    <h2 className="text-xl font-semibold mb-4">Charts</h2>
    <div className="h-48 bg-gray-100 rounded flex items-center justify-center">
      <span className="text-gray-500">Run a backtest to see charts</span>
    </div>
  </div>
)}
```

### 5. Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Basic UI components (button, input, etc.)
│   │   └── PlotlyChart.tsx  # Your custom charts
│   ├── pages/
│   │   └── Index.tsx        # Main dashboard page
│   ├── services/
│   │   └── api.ts          # Backend API calls
│   ├── App.tsx             # Simple app wrapper
│   └── main.tsx            # Entry point
├── package.json            # Simplified dependencies
└── README.md              # This guide
```

### 6. Running Everything

1. **Start Backend**: `conda activate quant && python src/api/server.py`
2. **Start Frontend**: `conda activate quant && cd frontend && npm run dev`
3. **Open Browser**: `http://localhost:5173`

### Common Tasks

- **Add new input**: Modify `src/pages/Index.tsx`, add state and form field
- **Change styling**: Edit Tailwind classes or add CSS to `src/App.css`
- **Add new chart**: Create component in `src/components/` and import in `Index.tsx`
- **Connect new backend endpoint**: Add function to `src/services/api.ts`

This simplified setup makes it easy to customize without getting lost in complex abstractions!

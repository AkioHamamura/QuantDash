Complete Data Flow Explanation
Now let me explain exactly how the data flows from backend to frontend:

1. User Clicks "Run Backtest" (Frontend)
User fills form with symbol, period, algorithm parameters
Frontend calls apiClient.runBacktest() with these parameters
HTTP POST request sent to http://localhost:8000/api/backtest
2. Backend Receives Request (server.py)
FastAPI receives POST request at /api/backtest endpoint
Extracts parameters from request body
Creates MovingAverageCrossover strategy instance
3. Backend Runs Backtest (engine.py)
BacktestEngine.run() is called with stock data
Strategy processes data through these steps:
preprocess_data(): Clean and prepare data
generate_signals(): Calculate moving averages and buy/sell signals
simulate_trading(): Execute trades and calculate performance
get_json_visualizations(): Create Plotly charts as JSON strings
4. Backend Creates Charts (ma_crossover.py)
Your get_json_visualizations() method:

Takes the results DataFrame with columns: Close, Buy_Signal, Sell_Signal, Portfolio_Value
Creates two Plotly figures:
Price Chart: Stock price + moving averages + buy/sell markers
Portfolio Chart: Portfolio value over time
Converts both figures to JSON strings using pio.to_json()
Returns: {"price_and_signals": "...", "portfolio_value": "..."}
5. Backend Returns JSON Response
6. Frontend Receives Response (Index.tsx)
result contains the backend response
Metrics go to setResults() for the dashboard
Visualizations go to setVisualizations() after JSON.parse()
7. Frontend Renders Charts
React re-renders due to state changes
<Plot> components receive parsed Plotly data
Charts display with interactive features (zoom, pan, hover)
Key Points for Learning:
JSON Serialization: Backend converts Python Plotly figures to JSON strings
State Management: Frontend uses separate state for metrics vs. charts
Conditional Rendering: Charts only show when data is available
Error Handling: Fallback placeholders if visualization data is missing
Responsive Design: Charts auto-resize with container
The beauty of this approach is that all the complex chart creation happens in Python (where you have powerful libraries), but the charts render as fully interactive JavaScript components in the browser!

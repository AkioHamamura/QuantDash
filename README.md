# QuantDash 📈

**Professional Algorithmic Trading Backtesting Platform**

A full-stack web application for backtesting algorithmic trading strategies with interactive visualizations and comprehensive performance analytics. Built with React frontend and FastAPI backend.

🚀 **[Live website: https://quantdash-playground.onrender.com](https://quantdash-playground.onrender.com)** 
PS! Website may take some time to boot up after inactivity as a result of using the free tier on Render.com

![QuantDash Logo](frontend/public/logo.png)

## 🎯 Overview

QuantDash provides a professional-grade platform for developing, testing, and analyzing algorithmic trading strategies. The platform features a modern web interface with real-time parameter adjustment, interactive charts, and detailed performance metrics.

### Key Features
- 🚀 **6 Pre-built Trading Strategies** - Ready-to-use algorithms with customizable parameters
- 📊 **Interactive Visualizations** - Real-time charts with Plotly integration
- 📈 **Comprehensive Analytics** - Sharpe ratio, Sortino ratio, max drawdown, win rate, and more
- 🎛️ **Live Parameter Tuning** - Adjust strategy parameters in real-time
- 📱 **Mobile Responsive** - Access from any device on your network
- 🎨 **Professional UI** - Modern, clean interface with gradient designs
- 🔄 **Real-time Data** - Live stock data integration with caching
- 📋 **Ticker Autocomplete** - Smart ticker search with validation

## 🏗️ Architecture

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React + TypeScript + Vite | Modern web interface |
| **Backend** | FastAPI + Python | High-performance API server |
| **Data Processing** | Pandas + NumPy | Financial data manipulation |
| **Data Source** | yfinance | Real-time stock data |
| **Visualization** | Plotly.js | Interactive charts |
| **Styling** | Tailwind CSS | Modern responsive design |
| **Caching** | Parquet files | High-performance data storage |

### Project Structure

```
QuantDash/
├── backend/                          # Python FastAPI backend
│   ├── src/
│   │   ├── strategies/              # Trading strategy implementations
│   │   │   ├── ma_crossover.py     # Moving Average Crossover
│   │   │   ├── bollinger_breakout.py # Bollinger Band Breakout
│   │   │   ├── dual_momentum.py    # Dual Momentum Strategy
│   │   │   ├── gap_fade.py         # Gap Fade Strategy
│   │   │   ├── rsi_pullback.py     # RSI Pullback Strategy
│   │   │   └── turtle_breakout.py  # Turtle Breakout Strategy
│   │   ├── backtesting/            # Backtesting engine
│   │   │   ├── engine.py          # Main backtesting logic
│   │   │   └── viz.py             # Visualization generation
│   │   ├── data/                   # Data fetching and caching
│   │   │   └── data_fetcher.py    # yfinance integration
│   │   ├── api/                    # FastAPI server
│   │   │   └── server.py          # API endpoints
│   │   └── utils/                  # Helper utilities
│   ├── cache/                      # Cached market data (Parquet)
│   └── main.py                     # Backend entry point
├── frontend/                        # React frontend
│   ├── src/
│   │   ├── pages/                  # React pages
│   │   │   └── Index.tsx          # Main trading interface
│   │   ├── services/               # API integration
│   │   │   └── api.ts             # Backend communication
│   │   └── components/             # Reusable components
│   ├── public/
│   │   └── logo.png               # QuantDash logo
│   ├── package.json               # NPM dependencies
│   └── vite.config.ts             # Vite configuration
├── config/
│   └── config.yaml                # Application configuration
├── docs/                          # Documentation
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ with conda/pip
- Node.js 18+ with npm
- Git

### 1. Clone Repository
```bash
git clone https://github.com/jakobildstad/QuantDash.git
cd QuantDash
```

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create conda environment (recommended)
conda create -n quant python=3.9
conda activate quant

# Install dependencies
pip install -r ../requirements.txt

# Start backend server
python src/controller/server.py
```

The backend will start on `http://localhost:8000`

### 3. Frontend Setup
```bash
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on `http://localhost:5173`

### 4. Access Application
- **Live Demo**: https://quantdash-frontend.onrender.com (Production deployment)
- **Local**: http://localhost:5173
- **Network**: http://YOUR_IP:5173 (for mobile access)

## 📊 Trading Strategies

### 1. Moving Average Crossover
**Strategy**: Buy when fast MA crosses above slow MA, sell when below
- **Parameters**: Fast Period (5-50), Slow Period (10-100)
- **Use Case**: Trend following in trending markets

### 2. Bollinger Band Breakout
**Strategy**: Trade breakouts above/below Bollinger Bands
- **Parameters**: Period (10-50), Standard Deviation (1.0-3.0)
- **Use Case**: Volatility breakouts and momentum trading

### 3. Dual Momentum
**Strategy**: Combine absolute and relative momentum signals
- **Parameters**: Lookback Period (20-120), Risk-Free Rate (0-10%)
- **Use Case**: Long-term trend following with risk management

### 4. Gap Fade
**Strategy**: Fade significant overnight gaps expecting mean reversion
- **Parameters**: Gap Threshold (1-5%), Stop Loss (2-10%)
- **Use Case**: Intraday mean reversion trading

### 5. RSI Pullback
**Strategy**: Buy oversold pullbacks in uptrends, sell overbought in downtrends
- **Parameters**: RSI Period (7-30), MA Period (20-100), Oversold/Overbought levels
- **Use Case**: Counter-trend trading with trend filter

### 6. Turtle Breakout
**Strategy**: Trade channel breakouts with ATR-based position sizing
- **Parameters**: Entry Period (10-50), Exit Period (5-30), ATR Period (10-30), Risk %
- **Use Case**: Systematic breakout trading with risk management

## 📈 Performance Metrics

QuantDash calculates comprehensive performance analytics:

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| **Total Return** | Overall percentage gain/loss | Higher is better |
| **Sharpe Ratio** | Risk-adjusted return | > 1.0 is good, > 2.0 is excellent |
| **Sortino Ratio** | Downside risk-adjusted return | Focuses on harmful volatility |
| **Max Drawdown** | Largest peak-to-trough decline | Lower is better (< -20% concerning) |
| **Volatility** | Annual price volatility | Strategy-dependent preference |
| **Win Rate** | Percentage of profitable trades | > 50% preferred for most strategies |
| **Total Trades** | Number of completed trades | Higher provides better statistics |

## 🔧 Configuration

### Environment Variables

**Frontend** (`.env.local`):
```bash
# API endpoint
VITE_API_BASE_URL=http://localhost:8000/api
```

**Backend Configuration** (`config/config.yaml`):
```yaml
data:
  cache_dir: "cache"
  default_period: "1y"
  
strategies:
  default_initial_cash: 10000
  
api:
  cors_origins:
    - "http://localhost:5173"
    - "http://10.0.0.116:5173"
```

### Customizing Strategies

Add new strategies by:

1. **Create strategy class** in `backend/src/strategies/`
2. **Inherit from BaseStrategy**
3. **Implement required methods**:
   - `generate_signals(data)`
   - `get_json_visualizations()`
4. **Register in server.py**

Example:
```python
class CustomStrategy(BaseStrategy):
    def __init__(self, param1=10, initial_cash=10000):
        super().__init__("Custom Strategy", initial_cash)
        self.param1 = param1
    
    def generate_signals(self, data):
        # Your strategy logic here
        pass
```

## 🌐 Deployment

### Local Network Access
1. **Find your IP**: `ipconfig getifaddr en0` (macOS) or `ipconfig` (Windows)
2. **Update environment**: Set `VITE_API_BASE_URL=http://YOUR_IP:8000/api`
3. **Restart servers**
4. **Access from mobile**: `http://YOUR_IP:5173`

### Production Deployment (Render.com)

**Live Application**: [https://quantdash-frontend.onrender.com](https://quantdash-frontend.onrender.com)

#### Backend Deployment:
1. **Create Web Service** on Render
2. **Connect GitHub** repository
3. **Set build command**: `pip install -r requirements.txt`
4. **Set start command**: `cd backend && python src/api/server.py`
5. **Add environment variables** as needed

#### Frontend Deployment:
1. **Create Static Site** on Render
2. **Set build command**: `cd frontend && npm install && npm run build`
3. **Set publish directory**: `frontend/dist`
4. **Add environment variable**: `VITE_API_BASE_URL=https://your-backend.onrender.com/api`

### Docker Deployment
```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "src/api/server.py"]
```

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing Checklist
- [ ] All 6 strategies load without errors
- [ ] Parameter changes update visualizations
- [ ] Charts display correctly
- [ ] Performance metrics calculate properly
- [ ] Mobile access works on network
- [ ] Ticker autocomplete functions
- [ ] Error handling works

## 🔍 API Documentation

### Endpoints

#### GET `/api/tickers`
Returns list of available stock tickers
```json
{
  "success": true,
  "tickers": ["AAPL", "GOOGL", "MSFT", ...]
}
```

#### GET `/api/strategies`
Returns available strategies and parameters
```json
{
  "success": true,
  "strategies": {
    "moving_average_crossover": {
      "name": "Moving Average Crossover",
      "parameters": {...}
    }
  }
}
```

#### POST `/api/backtest`
Run backtest with parameters
```json
{
  "symbol": "AAPL",
  "period": "1y",
  "algorithm": "moving_average_crossover",
  "initial_cash": 10000,
  "algorithm_specific_params": {
    "fast_period": 12,
    "slow_period": 26
  }
}
```

## 🐛 Troubleshooting

### Common Issues

**"Load failed" error**:
- Check backend server is running on port 8000
- Verify CORS settings allow your frontend URL
- Confirm environment variables are set correctly

**Charts not displaying**:
- Check browser console for JavaScript errors
- Verify Plotly.js is loaded correctly
- Ensure visualization data is valid JSON

**Mobile access not working**:
- Confirm both devices on same WiFi
- Update API URL to use IP address instead of localhost
- Check firewall/router settings

**Strategy errors**:
- Verify all required Python packages installed
- Check data availability for selected ticker
- Validate strategy parameters are in valid ranges

### Debug Mode
Enable detailed logging:
```bash
# Backend
export PYTHONPATH=$PYTHONPATH:./backend/src
python -m pdb backend/src/controller/server.py

# Frontend
npm run dev -- --debug
```

## � Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Add tests for new features
- Update documentation
- Ensure mobile compatibility

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **yfinance** for financial data
- **Plotly** for interactive visualizations
- **FastAPI** for high-performance backend
- **React** for modern frontend framework
- **Tailwind CSS** for beautiful styling

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/jakobildstad/QuantDash/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jakobildstad/QuantDash/discussions)
- **Email**: Contact through GitHub profile

---

**Built with ❤️ for algorithmic traders and quantitative analysts**

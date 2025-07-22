# QuantDash

An interactive web dashboard for backtesting algorithmic trading strategies and visualizing performance metrics.

## 🎯 Goal

Create an interactive web-dashboard that **back-tests algorithmic trading strategies** and visualizes key performance metrics (Sharpe, Sortino, equity-curve, drawdown).

## 🛠️ Core Stack

| Purpose | Tool |
| --- | --- |
| Data pull | `yfinance` |
| Data wrangle | `pandas` |
| Back-testing | `backtrader` |
| Interactivity & plots | `Plotly Dash` |
| Hosting | Streamlit Cloud **or** Render free tier |
| Version control | GitHub |

## 📁 Project Structure

```
QuantDash/
├── src/
│   ├── strategies/          # Trading strategy implementations
│   │   ├── ma_crossover.py      # Moving Average Crossover
│   │   ├── rsi_pullback.py      # RSI Pullback
│   │   ├── bollinger_breakout.py # Bollinger Band Breakout
│   │   ├── dual_momentum.py     # Dual Momentum
│   │   ├── gap_fade.py          # Gap Fade
│   │   ├── pair_trading.py      # Pair Trading
│   │   └── turtle_breakout.py   # Turtle Breakout
│   ├── data/                # Data fetching and processing
│   ├── backtesting/         # Backtesting engine and metrics
│   ├── dashboard/           # Dash web application
│   └── utils/               # Helper functions
├── config/                  # Configuration files (YAML)
├── data/                    # Historical price data (CSV)
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies
└── .gitignore              # Git ignore rules
```

## 🚀 Five-Night Sprint Plan

| Night | Deliverable | Key Tasks |
| --- | --- | --- |
| **Mon** | **Project scaffold** | Setup virtualenv, install dependencies, fetch SPY data |
| **Tue** | **Strategy & back-test** | Implement MA Crossover in backtrader, generate results |
| **Wed** | **Dashboard v0** | Build Dash app with charts and KPI cards |
| **Thu** | **Polish & docs** | Add controls, theme, write README + demo |
| **Fri** | **Deploy & share** | Deploy to cloud, share on social media |

## 📊 Available Strategies

1. **Moving Average Crossover** - Classic trend-following strategy
2. **RSI Pullback** - Mean reversion with trend filter
3. **Bollinger Band Breakout** - Volatility breakout strategy
4. **Dual Momentum** - Absolute and relative momentum
5. **Gap Fade** - Intraday mean reversion
6. **Pair Trading** - Statistical arbitrage
7. **Turtle Breakout** - Channel breakout system

## 🔧 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/jakobildstad/QuantDash.git
   cd QuantDash
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the dashboard**
   ```bash
   python src/main.py
   ```

## 📈 Features

- **Interactive Charts**: Price charts with technical indicators
- **Strategy Comparison**: Run multiple strategies simultaneously
- **Performance Metrics**: Sharpe ratio, Sortino ratio, max drawdown, etc.
- **Customizable Parameters**: Adjust strategy parameters in real-time
- **Data Export**: Download results and charts

## 🧪 Testing

```bash
pytest tests/
```

## 📝 License

This project is open source and available under the MIT License.

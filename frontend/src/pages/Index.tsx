import React, { useState, useEffect, useRef } from 'react';
import { apiClient } from '@/services/api'; // Adjust the import path as necessary
import Plot from 'react-plotly.js';


interface BacktestResults {
  strategy: string;
  parameters: any;
  total_return: number;
  final_value: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  volatility_pct: number;
  win_rate?: number;
  total_trades: number;
  portfolio_values: number[];
  trades: any[];
}

const Index = () => {
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('moving_average_crossover');
  const [symbol, setSymbol] = useState('AAPL');
  const [period, setPeriod] = useState('1y');
  const [initialCash, setInitialCash] = useState(10000);
  
  // Moving Average Crossover Parameters
  const [fastPeriod, setFastPeriod] = useState(12);
  const [slowPeriod, setSlowPeriod] = useState(26);
  
  // Bollinger Band Breakout Parameters
  const [bbPeriod, setBbPeriod] = useState(20);
  const [bbStdDev, setBbStdDev] = useState(2.0);
  
  // Dual Momentum Parameters
  const [dmLookbackPeriod, setDmLookbackPeriod] = useState(60);
  const [dmRiskFreeRate, setDmRiskFreeRate] = useState(0.02);
  
  // Gap Fade Parameters
  const [gfGapThreshold, setGfGapThreshold] = useState(0.02);
  const [gfStopLoss, setGfStopLoss] = useState(0.05);
  
  // RSI Pullback Parameters
  const [rsiPeriod, setRsiPeriod] = useState(14);
  const [rsiMaPeriod, setRsiMaPeriod] = useState(50);
  const [rsiOversold, setRsiOversold] = useState(30);
  const [rsiOverbought, setRsiOverbought] = useState(70);
  
  // Turtle Breakout Parameters
  const [tbEntryPeriod, setTbEntryPeriod] = useState(20);
  const [tbExitPeriod, setTbExitPeriod] = useState(10);
  const [tbAtrPeriod, setTbAtrPeriod] = useState(20);
  const [tbRiskPercent, setTbRiskPercent] = useState(0.02);
  
  const [results, setResults] = useState<BacktestResults | null>(null);
  const [loading, setLoading] = useState(false);
  
  // Add state for visualization data
  const [visualizations, setVisualizations] = useState<{
    price_and_signals?: any;
    portfolio_value?: any;
  }>({});

  // Autocomplete state
  const [availableTickers, setAvailableTickers] = useState<string[]>([]);
  const [filteredTickers, setFilteredTickers] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [inputFocused, setInputFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Load available tickers on component mount
  useEffect(() => {
    const loadTickers = async () => {
      const response = await apiClient.getAvailableTickers();
      if (response.success && response.tickers) {
        setAvailableTickers(response.tickers);
      }
    };
    loadTickers();
  }, []);

  // Filter tickers based on input
  useEffect(() => {
    if (availableTickers.length > 0) {
      if (symbol && symbol !== '') {
        // Filter based on input
        const filtered = availableTickers.filter(ticker => 
          ticker.toLowerCase().includes(symbol.toLowerCase())
        );
        setFilteredTickers(filtered.slice(0, 20)); // Show more results when filtering
        setShowDropdown(inputFocused && filtered.length > 0);
      } else {
        // Show all tickers when input is empty
        setFilteredTickers(availableTickers); // Show ALL tickers
        setShowDropdown(inputFocused);
      }
    } else {
      setFilteredTickers([]);
      setShowDropdown(false);
    }
  }, [symbol, availableTickers, inputFocused]);

  // Handle clicking outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node) &&
          inputRef.current && !inputRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
        setInputFocused(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSymbolChange = (value: string) => {
    // Only allow letters and convert to uppercase
    const validSymbol = value.replace(/[^A-Za-z]/g, '').toUpperCase();
    setSymbol(validSymbol);
  };

  const handleTickerSelect = (ticker: string) => {
    setSymbol(ticker);
    setShowDropdown(false);
    setInputFocused(false);
    inputRef.current?.blur();
  };

  const algorithms = [
    { value: 'moving_average_crossover', label: 'Moving Average Crossover' },
    { value: 'bollinger_breakout', label: 'Bollinger Band Breakout' },
    { value: 'dual_momentum', label: 'Dual Momentum' },
    { value: 'gap_fade', label: 'Gap Fade' },
    { value: 'rsi_pullback', label: 'RSI Pullback' },
    { value: 'turtle_breakout', label: 'Turtle Breakout' },
  ];

  const renderAlgorithmParameters = () => {
    switch (selectedAlgorithm) {
      case 'moving_average_crossover':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fast Period (Short Average)
              </label>
              <input
                type="number"
                value={fastPeriod}
                onChange={(e) => setFastPeriod(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="5"
                max="50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Slow Period (Long Average)
              </label>
              <input
                type="number"
                value={slowPeriod}
                onChange={(e) => setSlowPeriod(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="10"
                max="100"
              />
            </div>
          </>
        );
      case 'bollinger_breakout':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Period
              </label>
              <input
                type="number"
                value={bbPeriod}
                onChange={(e) => setBbPeriod(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="10"
                max="50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Standard Deviation Multiplier
              </label>
              <input
                type="number"
                value={bbStdDev}
                onChange={(e) => setBbStdDev(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="1.0"
                max="3.0"
                step="0.1"
              />
            </div>
          </>
        );
      case 'dual_momentum':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lookback Period
              </label>
              <input
                type="number"
                value={dmLookbackPeriod}
                onChange={(e) => setDmLookbackPeriod(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="20"
                max="120"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Risk-Free Rate
              </label>
              <input
                type="number"
                value={dmRiskFreeRate}
                onChange={(e) => setDmRiskFreeRate(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="0.0"
                max="0.1"
                step="0.01"
              />
            </div>
          </>
        );
      case 'gap_fade':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Gap Threshold (%)
              </label>
              <input
                type="number"
                value={gfGapThreshold}
                onChange={(e) => setGfGapThreshold(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="0.01"
                max="0.05"
                step="0.01"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Stop Loss (%)
              </label>
              <input
                type="number"
                value={gfStopLoss}
                onChange={(e) => setGfStopLoss(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="0.02"
                max="0.1"
                step="0.01"
              />
            </div>
          </>
        );
      case 'rsi_pullback':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                RSI Period
              </label>
              <input
                type="number"
                value={rsiPeriod}
                onChange={(e) => setRsiPeriod(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="7"
                max="30"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Moving Average Period
              </label>
              <input
                type="number"
                value={rsiMaPeriod}
                onChange={(e) => setRsiMaPeriod(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="20"
                max="100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Oversold Threshold
              </label>
              <input
                type="number"
                value={rsiOversold}
                onChange={(e) => setRsiOversold(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="20"
                max="40"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Overbought Threshold
              </label>
              <input
                type="number"
                value={rsiOverbought}
                onChange={(e) => setRsiOverbought(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="60"
                max="80"
              />
            </div>
          </>
        );
      case 'turtle_breakout':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Entry Period
              </label>
              <input
                type="number"
                value={tbEntryPeriod}
                onChange={(e) => setTbEntryPeriod(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="10"
                max="50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Exit Period
              </label>
              <input
                type="number"
                value={tbExitPeriod}
                onChange={(e) => setTbExitPeriod(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="5"
                max="30"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ATR Period
              </label>
              <input
                type="number"
                value={tbAtrPeriod}
                onChange={(e) => setTbAtrPeriod(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="10"
                max="30"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Risk Percent (%)
              </label>
              <input
                type="number"
                value={tbRiskPercent}
                onChange={(e) => setTbRiskPercent(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="0.01"
                max="0.05"
                step="0.01"
              />
            </div>
          </>
        );
      default:
        return null;
    }
  };

  const getAlgorithmParams = () => {
    switch (selectedAlgorithm) {
      case 'moving_average_crossover':
        return { fast_period: fastPeriod, slow_period: slowPeriod };
      case 'bollinger_breakout':
        return { period: bbPeriod, std_dev: bbStdDev };
      case 'dual_momentum':
        return { lookback_period: dmLookbackPeriod, risk_free_rate: dmRiskFreeRate };
      case 'gap_fade':
        return { gap_threshold: gfGapThreshold, stop_loss: gfStopLoss };
      case 'rsi_pullback':
        return { 
          rsi_period: rsiPeriod, 
          ma_period: rsiMaPeriod, 
          oversold: rsiOversold, 
          overbought: rsiOverbought 
        };
      case 'turtle_breakout':
        return { 
          entry_period: tbEntryPeriod, 
          exit_period: tbExitPeriod, 
          atr_period: tbAtrPeriod, 
          risk_percent: tbRiskPercent 
        };
      default:
        return { fast_period: fastPeriod, slow_period: slowPeriod };
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const algorithmParams = getAlgorithmParams();
      
      // API call would go here
      console.log('Running backtest with:', {
        symbol,
        period,
        algorithm: selectedAlgorithm,
        initial_cash: initialCash,
        algorithm_specific_params: algorithmParams
      });

      const result = await apiClient.runBacktest({ // Sends POST request to backend
        // The API expects these parameters:
        symbol: symbol,
        period: period,
        algorithm: selectedAlgorithm,
        initial_cash: initialCash,
        algorithm_specific_params: algorithmParams
      });
  
  // THE VALUES END UP HERE in 'result':
  console.log("Got result:", result);
    
    // USE THE ACTUAL API RESPONSE:
    if (result.success) {
      setResults({
        strategy: selectedAlgorithm,
        parameters: algorithmParams,
        total_return: result.data.total_return || 0,
        final_value: result.data.final_value || initialCash,
        sharpe_ratio: result.data.sharpe_ratio || 0, 
        sortino_ratio: result.data.sortino_ratio || 0, 
        max_drawdown: result.data.max_drawdown || 0, 
        volatility_pct: result.data.volatility_pct || 0,
        win_rate: result.data.win_rate || 0.0,
        total_trades: result.data.total_trades || 0,
        portfolio_values: result.data.portfolio_values || [],
        trades: result.data.trades || []
      });
      
      // Process visualization data from backend
      if (result.visualizations) {
        setVisualizations({
          price_and_signals: result.visualizations.price_and_signals ? 
            JSON.parse(result.visualizations.price_and_signals) : null,
          portfolio_value: result.visualizations.portfolio_value ? 
            JSON.parse(result.visualizations.portfolio_value) : null,
        });
      }
    } else {
      alert('Backtest failed: ' + result.error);
    }
    } catch (error) {
      console.error('Backtest failed:', error);
      alert('Failed to connect to backend: ' + error);
    } finally {
      setLoading(false);  // Always stop loading
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Modern Professional Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-6">
            <img 
              src="/logo.png" 
              alt="QuantDash Logo" 
              className="w-16 h-16 object-contain"
            />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 bg-clip-text text-transparent mb-3">
            QuantDash
          </h1>
          <p className="text-lg text-gray-600 font-medium">
            Professional Algorithmic Trading Backtesting Platform
          </p>
          <div className="w-24 h-1 bg-gradient-to-r from-blue-600 to-indigo-600 mx-auto mt-4 rounded-full"></div>
        </div>
        
        {/* Parameters Section */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-6">Parameters</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stock Symbol
                </label>
                <input
                  ref={inputRef}
                  type="text"
                  value={symbol}
                  onChange={(e) => handleSymbolChange(e.target.value)}
                  onFocus={() => setInputFocused(true)}
                  placeholder="AAPL"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  required
                />
                
                {/* Dropdown for autocomplete */}
                {showDropdown && (
                  <div 
                    ref={dropdownRef}
                    className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-y-auto"
                  >
                    {filteredTickers.map((ticker) => (
                      <div
                        key={ticker}
                        onClick={() => handleTickerSelect(ticker)}
                        className="px-3 py-2 cursor-pointer hover:bg-blue-50 hover:text-blue-600 transition-colors border-b border-gray-100 last:border-b-0"
                      >
                        {ticker}
                      </div>
                    ))}
                    {filteredTickers.length === 0 && (
                      <div className="px-3 py-2 text-gray-500 italic">
                        No tickers available
                      </div>
                    )}
                    {/* Show count of results */}
                    {filteredTickers.length > 0 && (
                      <div className="px-3 py-1 text-xs text-gray-500 bg-gray-50 border-t">
                        {filteredTickers.length} ticker{filteredTickers.length !== 1 ? 's' : ''} available
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Period
                </label>
                <select 
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white appearance-none cursor-pointer"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e")`,
                    backgroundPosition: 'right 8px center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: '16px 16px',
                    paddingRight: '32px'
                  }}
                >
                  <option value="6mo">6 Months</option>
                  <option value="1y">1 Year</option>
                  <option value="2y">2 Years</option>
                  <option value="3y">3 Years</option>
                  <option value="4y">4 Years</option>
                  <option value="5y">5 Years</option>
                  <option value="max">Max Available</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Initial Cash
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span className="text-gray-500 text-sm">$</span>
                  </div>
                  <input
                    type="number"
                    value={initialCash}
                    onChange={(e) => setInitialCash(Number(e.target.value))}
                    className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    min="1000"
                    step="1000"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Trading Algorithm
              </label>
              <select 
                value={selectedAlgorithm}
                onChange={(e) => setSelectedAlgorithm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white appearance-none cursor-pointer"
                style={{
                  backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e")`,
                  backgroundPosition: 'right 8px center',
                  backgroundRepeat: 'no-repeat',
                  backgroundSize: '16px 16px',
                  paddingRight: '32px'
                }}
              >
                {algorithms.map((algo) => (
                  <option key={algo.value} value={algo.value}>
                    {algo.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Algorithm-specific parameters */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {renderAlgorithmParameters()}
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Running Backtest...' : 'Run Backtest'}
            </button>
          </form>
        </div>

        {/* Results Section */}
        {results && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-6">Backtest Results</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className={`text-2xl font-bold ${results.final_value > initialCash ? 'text-green-600' : 'text-red-600'}`}>
                  ${results.final_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className="text-sm text-gray-600">Portfolio Value</div>
              </div>
              
              {results.win_rate !== undefined && (
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className={`text-2xl font-bold ${results.win_rate > 50 ? 'text-green-600' : 'text-red-600'}`}>
                    {results.win_rate.toFixed(2)}%
                  </div>
                  <div className="text-sm text-gray-600">Win Rate</div>
                </div>
              )}
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-black">
                  {results.total_trades}
                </div>
                <div className="text-sm text-gray-600">Total Trades</div>
              </div>

              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-black">
                  {results.volatility_pct.toFixed(2)}%
                </div>
                <div className="text-sm text-gray-600">Volatility</div>
              </div>

              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className={`text-2xl font-bold ${results.total_return > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {results.total_return > 0 ? '+' : ''}{results.total_return.toFixed(2)}%
                </div>
                <div className="text-sm text-gray-600">Total Return</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className={`text-2xl font-bold ${results.sharpe_ratio > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {results.sharpe_ratio.toFixed(2)}
                </div>
                <div className="text-sm text-gray-600">Sharpe Ratio</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className={`text-2xl font-bold ${results.sortino_ratio > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {results.sortino_ratio.toFixed(2)}
                </div>
                <div className="text-sm text-gray-600">Sortino Ratio</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className={`text-2xl font-bold ${results.max_drawdown > -20 ? 'text-green-600' : 'text-red-600'}`}>
                  {results.max_drawdown.toFixed(2)}%
                </div>
                <div className="text-sm text-gray-600">Max Drawdown</div>
              </div>
            </div>
          </div>
        )}

        {/* Charts Section */}
        {results && (
          <>
            {/* Portfolio Value Chart */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Portfolio Value Over Time</h2>
              {visualizations.portfolio_value ? (
                <Plot
                  data={visualizations.portfolio_value.data}
                  layout={{
                    ...visualizations.portfolio_value.layout,
                    autosize: true,
                    height: 400,
                  }}
                  useResizeHandler={true}
                  style={{ width: "100%", height: "400px" }}
                />
              ) : (
                <div className="h-80 bg-gray-100 rounded flex items-center justify-center">
                  <span className="text-gray-500">Portfolio value chart will appear here</span>
                </div>
              )}
            </div>

            {/* Price and Signals Chart */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Price Chart with Trading Signals</h2>
              {visualizations.price_and_signals ? (
                <Plot
                  data={visualizations.price_and_signals.data}
                  layout={{
                    ...visualizations.price_and_signals.layout,
                    autosize: true,
                    height: 400,
                  }}
                  useResizeHandler={true}
                  style={{ width: "100%", height: "400px" }}
                />
              ) : (
                <div className="h-80 bg-gray-100 rounded flex items-center justify-center">
                  <span className="text-gray-500">Price chart with buy/sell signals will appear here</span>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Index;

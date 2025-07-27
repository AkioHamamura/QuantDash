import React, { useState } from 'react';
import { apiClient } from '@/services/api'; // Adjust the import path as necessary
//import Plot from 'react-plotly.js';


interface BacktestResults {
  strategy: string;
  parameters: any;
  total_return: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  volatility_pct: number;
  win_rate?: number;
  profit_factor?: number;
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
  
  const [results, setResults] = useState<BacktestResults | null>(null);
  const [loading, setLoading] = useState(false);

  const algorithms = [
    { value: 'moving_average_crossover', label: 'Moving Average Crossover' },
    // Add more algorithms here as they become available
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
                min="1"
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
                min="1"
                max="200"
              />
            </div>
          </>
        );
      default:
        return null;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // API call would go here
      console.log('Running backtest with:', {
        symbol,
        period,
        algorithm: selectedAlgorithm,
        initial_cash: initialCash,
        algorithm_specific_params: {
          fast_period: fastPeriod,
          slow_period: slowPeriod,
        }
      });

      const result = await apiClient.runBacktest({
        symbol: symbol,
        period: period,
        algorithm: selectedAlgorithm,
        initial_cash: initialCash,
        algorithm_specific_params: {
          fast_period: fastPeriod,
          slow_period: slowPeriod,
        }
      });
  
  // THE VALUES END UP HERE in 'result':
  console.log("Got result:", result);
    
    // USE THE ACTUAL API RESPONSE:
    if (result.success) {
      setResults({
        strategy: selectedAlgorithm,
        parameters: { fast_period: fastPeriod, slow_period: slowPeriod },
        total_return: result.data.total_return || 0,
        sharpe_ratio: result.data.sharpe_ratio || 0, 
        sortino_ratio: result.data.sortino_ratio || 0, 
        max_drawdown: result.data.max_drawdown || 0, 
        volatility_pct: result.data.volatility_pct || 0,
        win_rate: result.data.win_rate || NaN,
        profit_factor: result.data.profit_factor || 0,
        portfolio_values: result.data.portfolio_values || [],
        trades: result.data.trades || []
      });
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
        <h1 className="text-3xl font-bold text-black-900 text-center mb-8">
          QuantDash - Backtest Your Trading Strategies
        </h1>
        
        {/* Parameters Section */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-6">Parameters</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stock Symbol
                </label>
                <input
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  placeholder="AAPL"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Period
                </label>
                <select 
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="1y">1 Year</option>
                  <option value="2y">2 Years</option>
                  <option value="5y">5 Years</option>
                  <option value="max">Max Available</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Initial Cash
                </label>
                <input
                  type="number"
                  value={initialCash}
                  onChange={(e) => setInitialCash(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  min="1000"
                  step="1000"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Algorithm
              </label>
              <select 
                value={selectedAlgorithm}
                onChange={(e) => setSelectedAlgorithm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
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
                <div className="text-2xl font-bold text-blue-600">
                  {results.total_return > 0 ? '+' : ''}{results.total_return.toFixed(2)}%
                </div>
                <div className="text-sm text-gray-600">Total Return</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {results.sharpe_ratio.toFixed(2)}
                </div>
                <div className="text-sm text-gray-600">Sharpe Ratio</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {results.sortino_ratio.toFixed(2)}
                </div>
                <div className="text-sm text-gray-600">Sortino Ratio</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {results.max_drawdown.toFixed(2)}%
                </div>
                <div className="text-sm text-gray-600">Max Drawdown</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {results.volatility_pct.toFixed(2)}%
                </div>
                <div className="text-sm text-gray-600">Volatility</div>
              </div>
              
              {results.win_rate && (
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {results.win_rate.toFixed(2)}%
                  </div>
                  <div className="text-sm text-gray-600">Win Rate</div>
                </div>
              )}
              
              {results.profit_factor && (
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {results.profit_factor.toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-600">Profit Factor</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Charts Section */}
        {results && (
          <>
            {/* Portfolio Value Chart */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Portfolio Value Over Time</h2>
              <div className="h-80 bg-gray-100 rounded flex items-center justify-center">
                <span className="text-gray-500">Portfolio value chart will appear here</span>
              </div>
            </div>

            {/* Price and Signals Chart */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Price Chart with Trading Signals</h2>
              <div className="h-80 bg-gray-100 rounded flex items-center justify-center">
                <span className="text-gray-500">Price chart with buy/sell signals will appear here</span>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Index;

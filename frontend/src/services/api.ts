// Simple API service for QuantDash backend
// Use environment variable for production, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export interface BacktestRequest {
  symbol: string;
  period?: string;
  algorithm: string;
  initial_cash?: number; // Initial cash for the backtest
  algorithm_specific_params?: Record<string, any>;
}

export interface BacktestResponse {
  success: boolean;
  data?: {
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
  };
  visualizations?: {
    price_and_signals: string;  // JSON string from plotly
    portfolio_value: string;    // JSON string from plotly
  };
  results?: any; // Keep for backward compatibility
  plot?: string; // URL to the plot image
  error?: string;
}

export const apiClient = {
  async runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/backtest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  },

  // Get available stock tickers
  async getAvailableTickers(): Promise<{success: boolean; tickers?: string[]; error?: string}> {
    try {
      const response = await fetch(`${API_BASE_URL}/tickers`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  },
  // Add more API methods as needed
};
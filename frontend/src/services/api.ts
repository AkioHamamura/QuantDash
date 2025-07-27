// Simple API service for QuantDash backend
const API_BASE_URL = 'http://localhost:8000/api';

export interface BacktestRequest {
  symbol: string;
  period?: string;
  strategy_params?: Record<string, any>;
}

export interface BacktestResponse {
  success: boolean;
  data?: any;
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

  async getStockData(symbol: string, period: string = '1y') {
    try {
      const response = await fetch(`${API_BASE_URL}/stocks/${symbol}/data?period=${period}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch stock data:', error);
      return null;
    }
  },
};

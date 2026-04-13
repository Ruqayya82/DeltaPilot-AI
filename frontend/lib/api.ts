// API client for communicating with the DeltaPilot backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface PriceData {
  symbol: string;
  price: number;
}

export interface Signal {
  id: string;
  symbol: string;
  signal: string;
  price: number;
  confidence: number;
  created_at: string;
}

export interface Trade {
  id: string;
  symbol: string;
  side: string;
  entry_price: number;
  stop_loss?: number;
  take_profit?: number;
  size?: number;
  status: string;
  created_at: string;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Market Data
  async getPrice(symbol: string): Promise<PriceData> {
    return this.request<PriceData>(`/api/market/price/${symbol}`);
  }

  async getBars(symbol: string, timeframe: string = '1D', limit: number = 100) {
    return this.request(`/api/market/bars/${symbol}?timeframe=${timeframe}&limit=${limit}`);
  }

  async getQuotes(symbols: string[]) {
    return this.request(`/api/market/quotes?symbols=${symbols.join(',')}`);
  }

  // Signals
  async generateSignal(symbol: string, prices: number[]): Promise<Signal> {
    return this.request<Signal>('/api/signals/generate', {
      method: 'POST',
      body: JSON.stringify({ symbol, prices }),
    });
  }

  async getSignals(): Promise<Signal[]> {
    return this.request<Signal[]>('/api/signals/');
  }

  async createSignal(signal: Omit<Signal, 'id' | 'created_at'>): Promise<Signal> {
    return this.request<Signal>('/api/signals/', {
      method: 'POST',
      body: JSON.stringify(signal),
    });
  }

  // Trading
  async getAccount() {
    return this.request('/api/trading/account');
  }

  async getPositions() {
    return this.request('/api/trading/positions');
  }

  async placeOrder(order: {
    symbol: string;
    side: string;
    type: string;
    qty: number;
    time_in_force: string;
  }) {
    return this.request('/api/trading/order', {
      method: 'POST',
      body: JSON.stringify(order),
    });
  }

  // Authentication
  async register(email: string, password: string) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async login(email: string, password: string) {
    return this.request('/auth/jwt/login', {
      method: 'POST',
      body: JSON.stringify({ username: email, password }),
    });
  }
}

export const apiClient = new ApiClient();
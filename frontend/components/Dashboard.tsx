"use client";

import { useEffect, useState, useCallback } from 'react';
import PriceChart from './PriceChart';
import PortfolioCard from './PortfolioCard';
import MarketOverview from './MarketOverview';
import TradePanel from './TradePanel';
import { apiClient } from '../lib/api';

interface PriceData {
  symbol: string;
  price: number;
}

interface Position {
  symbol: string;
  qty: number;
  avg_entry_price: number;
  market_value: number;
  unrealized_pl: number;
  unrealized_plpc: number;
}

interface Account {
  buying_power: string;
  portfolio_value: string;
  equity: string;
}

function DashboardContent({
  price,
  account,
  positions,
  signals,
  buySymbol,
  buyQty,
  sellSymbol,
  sellQty,
  setBuySymbol,
  setBuyQty,
  setSellSymbol,
  setSellQty,
  placeOrder
}: {
  price: PriceData | null;
  account: Account | null;
  positions: Position[];
  signals: any[];
  buySymbol: string;
  buyQty: number;
  sellSymbol: string;
  sellQty: number;
  setBuySymbol: (s: string) => void;
  setBuyQty: (q: number) => void;
  setSellSymbol: (s: string) => void;
  setSellQty: (q: number) => void;
  placeOrder: (side: 'buy' | 'sell', symbol: string, qty: number) => Promise<void>;
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-[#1F1F23] text-white h-[80px] flex items-center px-5 shadow-lg">
        <div className="max-w-7xl mx-auto w-full flex justify-between items-center">
          <h1 className="text-2xl font-bold">DeltaPilot AI</h1>
          <nav className="flex gap-4">
            <button className="px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors">Portfolio</button>
            <button className="px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors">
              Signals ({signals.length})
            </button>
            <button className="px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors">Trades</button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1440px] mx-auto p-6">
        {/* Top Row: Portfolio and Market Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <PortfolioCard account={account} positions={positions} />
          <MarketOverview />
        </div>

        {/* Price Chart */}
        <div className="mb-8">
          <PriceChart />
        </div>

        {/* Trade Panel */}
        <TradePanel
          buySymbol={buySymbol}
          setBuySymbol={setBuySymbol}
          buyQty={buyQty}
          setBuyQty={setBuyQty}
          sellSymbol={sellSymbol}
          setSellSymbol={setSellSymbol}
          sellQty={sellQty}
          setSellQty={setSellQty}
          placeOrder={placeOrder}
          account={account}
          price={price}
        />
      </main>
    </div>
  );
}

export default function Dashboard() {
  const [price, setPrice] = useState<PriceData | null>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [account, setAccount] = useState<Account | null>(null);
  const [positions, setPositions] = useState<any[]>([]);
  const [buySymbol, setBuySymbol] = useState("AAPL");
  const [buyQty, setBuyQty] = useState(1);
  const [sellSymbol, setSellSymbol] = useState("AAPL");
  const [sellQty, setSellQty] = useState(1);

  const fetchPrice = useCallback(async () => {
    try {
      const data = await apiClient.getPrice('AAPL');
      setPrice(data);
    } catch (error) {
      console.error('Price fetch error:', error);
    }
  }, []);

  const fetchSignals = useCallback(async () => {
    const res = await fetch('http://localhost:8000/api/signals/');
    const data = await res.json();
    setSignals(data);
  }, []);

  const fetchAccount = useCallback(async () => {
    const res = await fetch('http://localhost:8000/api/trading/account');
    const data = await res.json();

    setAccount({
      buying_power: parseFloat(data.buying_power || '0').toLocaleString(),
      portfolio_value: parseFloat(data.portfolio_value || '0').toLocaleString(),
      equity: parseFloat(data.equity || '0').toLocaleString()
    });
  }, []);

  const fetchPositions = useCallback(async () => {
    const res = await fetch('http://localhost:8000/api/trading/positions');
    const data = await res.json();
    setPositions(data);
  }, []);

  const fetchAllData = useCallback(async () => {
    await Promise.all([
      fetchPrice(),
      fetchSignals(),
      fetchAccount(),
      fetchPositions()
    ]);
  }, [fetchPrice, fetchSignals, fetchAccount, fetchPositions]);

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 5000);
    return () => clearInterval(interval);
  }, [fetchAllData]);

  const placeOrder = async (side: 'buy' | 'sell', symbol: string, qty: number) => {
    try {
      const res = await fetch('http://localhost:8000/api/trading/order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, side, qty })
      });

      if (res.ok) {
        alert(`${side.toUpperCase()} order placed!`);
        fetchPositions();
        fetchAccount();
      } else {
        alert('Order failed');
      }
    } catch (error) {
      alert('Order error');
    }
  };

  return (
    <DashboardContent
      price={price}
      account={account}
      positions={positions}
      signals={signals}
      buySymbol={buySymbol}
      buyQty={buyQty}
      sellSymbol={sellSymbol}
      sellQty={sellQty}
      setBuySymbol={setBuySymbol}
      setBuyQty={setBuyQty}
      setSellSymbol={setSellSymbol}
      setSellQty={setSellQty}
      placeOrder={placeOrder}
    />
  );
}
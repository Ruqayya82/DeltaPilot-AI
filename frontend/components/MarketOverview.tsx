"use client";

import { useEffect, useState } from 'react';
import { usePriceWebSocket } from '../lib/usePriceWebSocket';

interface Quote {
  symbol: string;
  price: number;
}

export default function MarketOverview() {
  const { prices, isConnected } = usePriceWebSocket();
  const [prevPrices, setPrevPrices] = useState<Record<string, number>>({});

  // Update previous prices when new prices arrive
  useEffect(() => {
    setPrevPrices(currentPrev => ({ ...currentPrev, ...prices }));
  }, [prices]);

  const getChangePercent = (symbol: string, currentPrice: number): number => {
    const prev = prevPrices[symbol];
    return prev && prev !== currentPrice ? ((currentPrice - prev) / prev * 100) : 0;
  };

  const symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT'] as const;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 h-[300px] w-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">Top Market Assets</h2>
        <div className={`flex items-center gap-2 text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-600' : 'bg-red-600'}`}></div>
          {isConnected ? 'Live' : 'Disconnected'}
        </div>
      </div>
      <div className="grid grid-cols-1 gap-3 overflow-y-auto h-[200px]">
        {symbols.map((symbol) => {
          const price = prices[symbol];
          const displayPrice = price ? price.toFixed(2) : 'N/A';
          const change = price ? getChangePercent(symbol, price) : 0;
          const changeStr = change.toFixed(1);
          const isPositive = change >= 0;
          const changeColor = isPositive ? 'text-emerald-600' : 'text-red-600';

          return (
            <div key={symbol} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg border hover:bg-gray-100 transition-colors">
              <span className="font-medium text-gray-900 text-lg">{symbol}</span>
              <span className="font-semibold text-gray-900 text-lg flex items-center gap-1">
                ${displayPrice}
                {price && (
                  <span className={`ml-1 ${changeColor} font-bold`}>
                    {isPositive ? '+' : ''}{changeStr}%
                  </span>
                )}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

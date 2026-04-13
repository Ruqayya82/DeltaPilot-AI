"use client";

interface Account {
  buying_power: string;
  equity: string;
}

interface PriceData {
  symbol: string;
  price: number;
}

interface TradePanelProps {
  buySymbol: string;
  setBuySymbol: (value: string) => void;
  buyQty: number;
  setBuyQty: (value: number) => void;
  sellSymbol: string;
  setSellSymbol: (value: string) => void;
  sellQty: number;
  setSellQty: (value: number) => void;
  placeOrder: (side: 'buy' | 'sell', symbol: string, qty: number) => Promise<void>;
  account?: Account | null;
  price?: PriceData | null;
}

export default function TradePanel({
  buySymbol,
  setBuySymbol,
  buyQty,
  setBuyQty,
  sellSymbol,
  setSellSymbol,
  sellQty,
  setSellQty,
  placeOrder,
  account,
  price,
}: TradePanelProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 h-[140px]">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
        {/* Buy Section */}
        <div className="bg-green-50 border-2 border-dashed border-green-200 rounded-2xl p-4 flex items-center justify-center">
          <div className="w-full max-w-md">
            <h3 className="text-xl font-bold text-green-800 mb-2">BUY</h3>
            <div className="flex gap-2">
              <input
                type="text"
                value={buySymbol}
                onChange={(e) => setBuySymbol(e.target.value.toUpperCase())}
                placeholder="Symbol"
                className="flex-1 p-2 border border-green-300 rounded-lg text-center font-mono text-sm"
              />
              <input
                type="number"
                value={buyQty}
                onChange={(e) => setBuyQty(parseFloat(e.target.value) || 0)}
                placeholder="Qty"
                className="w-20 p-2 border border-green-300 rounded-lg text-center font-mono text-sm"
              />
              <button
                onClick={() => placeOrder('buy', buySymbol, buyQty)}
                disabled={!buySymbol || buyQty <= 0}
                className="px-6 py-2 bg-green-600 text-white rounded-lg font-bold hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                Buy
              </button>
            </div>
          </div>
        </div>

        {/* Sell Section */}
        <div className="bg-red-50 border-2 border-dashed border-red-200 rounded-2xl p-4 flex items-center justify-center">
          <div className="w-full max-w-md">
            <h3 className="text-xl font-bold text-red-800 mb-2">SELL</h3>
            <div className="flex gap-2">
              <input
                type="text"
                value={sellSymbol}
                onChange={(e) => setSellSymbol(e.target.value.toUpperCase())}
                placeholder="Symbol"
                className="flex-1 p-2 border border-red-300 rounded-lg text-center font-mono text-sm"
              />
              <input
                type="number"
                value={sellQty}
                onChange={(e) => setSellQty(parseFloat(e.target.value) || 0)}
                placeholder="Qty"
                className="w-20 p-2 border border-red-300 rounded-lg text-center font-mono text-sm"
              />
              <button
                onClick={() => placeOrder('sell', sellSymbol, sellQty)}
                disabled={!sellSymbol || sellQty <= 0}
                className="px-6 py-2 bg-red-600 text-white rounded-lg font-bold hover:bg-red-700 disabled:opacity-50 transition-colors"
              >
                Sell
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


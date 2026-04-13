"use client";

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
  equity: string;
}

interface PortfolioCardProps {
  account: Account | null;
  positions: Position[];
}

export default function PortfolioCard({ account, positions }: PortfolioCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 h-[300px] w-full">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Portfolio</h2>
        {account ? (
          <div className="text-right">
            <div className="text-sm text-gray-600">Equity: ${account.equity}</div>
            <div className="text-lg font-bold text-emerald-600">Buying Power: ${account.buying_power}</div>
          </div>
        ) : (
          <div className="text-right text-sm text-gray-500">Loading account…</div>
        )}
      </div>
      <div className="overflow-x-auto h-[200px]">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-gray-50">
              <th className="text-left py-3 px-4 font-semibold text-gray-900">Asset</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-900">Qty</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-900">Avg Price</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-900">Market Value</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-900">P&L</th>
            </tr>
          </thead>
          <tbody>
            {positions.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-gray-500 font-medium">No open positions</td>
              </tr>
            ) : (
              positions.map((pos: Position) => (
                <tr key={pos.symbol} className="border-b hover:bg-gray-50 transition-colors">
                  <td className="py-4 px-4 font-semibold text-gray-900">{pos.symbol}</td>
                  <td className="py-4 px-4 text-gray-900">{pos.qty}</td>
                  <td className="py-4 px-4 text-gray-900">${pos.avg_entry_price.toFixed(2)}</td>
                  <td className="py-4 px-4 text-gray-900">${pos.market_value.toFixed(2)}</td>
                  <td className="py-4 px-4">
                    <span className={pos.unrealized_pl >= 0 ? "text-emerald-600 font-semibold" : "text-red-600 font-semibold"}>
                      ${pos.unrealized_pl.toFixed(2)} ({(pos.unrealized_plpc * 100).toFixed(1)}%)
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}


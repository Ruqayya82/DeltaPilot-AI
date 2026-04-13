"use client";

import { useEffect, useRef, useState } from 'react';

interface PriceChartProps {
  symbol?: string;
}

interface ChartDataPoint {
  time: number;
  price: number;
}

export default function PriceChart({ symbol = 'AAPL' }: PriceChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchChartData = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`http://localhost:8000/api/market/bars/${symbol}?timeframe=1Min&limit=50`);
      if (!response.ok) throw new Error('Failed to fetch bars');
      const data = await response.json();
      // Transform the data for the chart
      const bars = data?.bars ?? [];
      const transformedData = Array.isArray(bars) ? bars.slice().reverse().map((bar: any, i: number) => ({
        time: i,
        price: bar.close
      })) : [];
      setChartData(transformedData);
    } catch (error) {
      console.error('Chart data fetch error:', error);
      // Fallback to mock data
      const mockData = generateMockData();
      setChartData(mockData);
    } finally {
      setIsLoading(false);
    }
  };

  const generateMockData = (): ChartDataPoint[] => {
    const data = [];
    const base = 175;
    for (let i = 0; i < 50; i++) {
      data.push({
        time: i,
        price: base + (Math.sin(i / 5) * 2) + (Math.random() - 0.5) * 1.5
      });
    }
    return data;
  };

  useEffect(() => {
    fetchChartData();
    const interval = setInterval(fetchChartData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [symbol]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || chartData.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Light background
    ctx.fillStyle = '#F8FAFC';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Grid lines
    ctx.strokeStyle = '#E2E8F0';
    ctx.lineWidth = 1;
    for (let i = 0; i < canvas.height; i += 40) {
      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(canvas.width, i);
      ctx.stroke();
    }
    for (let i = 0; i < canvas.width; i += 80) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, canvas.height);
      ctx.stroke();
    }

    // Price line
    ctx.strokeStyle = '#3B82F6';
    ctx.lineWidth = 3;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.beginPath();

    const maxPrice = Math.max(...chartData.map(d => d.price));
    const minPrice = Math.min(...chartData.map(d => d.price));
    const range = maxPrice - minPrice || 1;

    chartData.forEach((point, i) => {
      const x = (i / (chartData.length - 1)) * (canvas.width - 40) + 20;
      const y = canvas.height - ((point.price - minPrice) / range * (canvas.height - 40)) - 20;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Price labels
    ctx.fillStyle = '#64748B';
    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'right';
    [minPrice, (minPrice + maxPrice)/2, maxPrice].forEach((p, i) => {
      const y = canvas.height - (i * (canvas.height - 40) / 2) - 10;
      ctx.fillText(`$${p.toFixed(2)}`, 15, y);
    });
  }, [chartData]);

  return (
    <div className="w-full h-[300px] bg-white rounded-xl border border-gray-200 shadow-sm p-4">
      {isLoading && (
        <div className="flex items-center justify-center h-full">
          <div className="text-gray-500">Loading chart...</div>
        </div>
      )}
      <canvas
        ref={canvasRef}
        width={1400}
        height={300}
        className="w-full h-full max-w-[1400px] mx-auto"
      />
    </div>
  );
}

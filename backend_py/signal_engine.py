import numpy as np
import pandas as pd

def generate_signal(prices: list[float]) -> str:
    """
    Ported from original JS: Simple MA crossover (5 short / 20 long).
    """
    if len(prices) < 20:
        return "HOLD"
    
    df = pd.Series(prices)
    short_ma = df.tail(5).mean()
    long_ma = df.tail(20).mean()
    
    if short_ma > long_ma:
        return "BUY"
    elif short_ma < long_ma:
        return "SELL"
    return "HOLD"

def average(arr: list[float]) -> float:
    return np.mean(arr)


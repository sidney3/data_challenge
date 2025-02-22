from __future__ import annotations

class Config:
    """
    Config related to the trading system.
    """
    tickers : list[str] = ["AAPL"]

    smoothing_factor: float = 0.5

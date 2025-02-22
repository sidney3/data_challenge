from __future__ import annotations

from datetime import datetime, timedelta

class Config:
    """
    Config related to the trading system.
    """
    tickers : list[str] = ["AAPL"]

    smoothing_factor: float = 0.5

    trade_every: timedelta = timedelta(milliseconds=250)

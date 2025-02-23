from __future__ import annotations

from datetime import datetime, timedelta

class Config:
    """
    Config related to the trading system.
    """
    tickers : list[str] = ["A", "B", "C", "D", "E"]

    smoothing_factor: float = 0.5

    change_our_position_within: float = 3

    close_all_positions_limit: float = 10

    # if the fair value falls at least this constant outside our
    # posted range, pull all of our orders.
    close_position_if_this_far_outside: float = 3

    rate_limit = timedelta(seconds=2)

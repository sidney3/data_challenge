from __future__ import annotations

import pandas as pd
from gt_trading_client import SharedState

class PricingEngine:
    def __init__(self, shared_state: SharedState, historical_data: pd.DataFrame):
        """
        The format of the historical data:

        a time series dataframe (indexed by tick) with columns for
        each symbol.

        historical_data.iloc[0]["AAPL"] will give the price of 
        "AAPL" at tick 0
        """
        pass
    def on_tick(self):
        pass
    def fair_values(self) -> dict[str, float]:
        return {}

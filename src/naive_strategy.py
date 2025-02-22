from __future__ import annotations

from gt_trading_client import Prioritizer
from gt_trading_client import SharedState
from gt_trading_client import Strategy

from config import Config
from pricing_engine import PricingEngine

import pandas as pd
import time
import asyncio

class NaiveStrategy(Strategy):
    pricing_engine: PricingEngine
    def __init__(self, quoter: Prioritizer, shared_state: SharedState, config: Config, historical_data: pd.DataFrame):
        super().__init__(quoter, shared_state)
        self.pricing_engine = PricingEngine(shared_state, historical_data, config)

    async def on_orderbook_update(self) -> None:
        print("Orderbook update", self._cnt, time.time())
        self.pricing_engine.on_tick()
        pass

    async def on_portfolio_update(self) -> None:
        print("Portfolio update", self._cnt, time.time())
        print(self._shared_state.portfolio.positions)
        pass

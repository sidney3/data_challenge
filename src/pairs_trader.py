from __future__ import annotations

from gt_trading_client import Prioritizer
from gt_trading_client import SharedState
from gt_trading_client import Strategy

import time
import asyncio
import pandas as pd

class MeanReversionStrategy(Strategy):
    def __init__(self, quoter: Prioritizer, shared_state: SharedState, historical_data: pd.DataFrame):
        super().__init__(quoter, shared_state)
        self._cnt = 1

    async def on_orderbook_update(self) -> None:
        print("Orderbook update", self._cnt, time.time())
        # asyncio.create_task(self._quoter.remove_all())
        asyncio.create_task(self._quoter.place_limit(ticker="A", volume=1, price=50+self._cnt, is_bid=True))
        asyncio.create_task(self._quoter.place_limit(ticker="A", volume=1, price=950-self._cnt, is_bid=False))
        # asyncio.create_task(self._quoter.place_market(ticker="A", volume=1, is_bid=True))
        # asyncio.create_task(self._quoter.place_market(ticker="A", volume=1, is_bid=False))
        self._cnt += 1

    async def on_portfolio_update(self) -> None:
        print("Portfolio update", self._cnt, time.time())
        print(self._shared_state.portfolio.positions)
        pass

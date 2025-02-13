from __future__ import annotations

from gt_trading_client import Prioritizer
from gt_trading_client import SharedState
from gt_trading_client import Strategy

import time
import asyncio


class TestStrategy(Strategy):
    def __init__(self, quoter: Prioritizer, shared_state: SharedState):
        super().__init__(quoter, shared_state)
        self._cnt = 1

    async def on_orderbook_update(self) -> None:
        print("Orderbook update", self._cnt, time.time())
        print(self._shared_state.orderbook.best_bid("A"))
        print(self._shared_state.orderbook.best_ask("A"))
        # asyncio.create_task(self._quoter.remove_all()) # non-blocking
        # await self._quoter.remove_all() # blocking
        asyncio.create_task(self._quoter.place_limit(ticker="A", volume=1, price=951-self._cnt, is_bid=False))
        asyncio.create_task(self._quoter.place_limit(ticker="A", volume=1, price=49+self._cnt, is_bid=True))
        self._cnt += 1

    async def on_portfolio_update(self) -> None:
        print("Portfolio update", self._cnt, time.time())
        pass

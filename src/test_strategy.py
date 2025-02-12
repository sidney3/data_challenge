from __future__ import annotations

from gt_trading_client import Prioritizer
from gt_trading_client import SharedState
from gt_trading_client import Strategy

import time


class TestStrategy(Strategy):
    def __init__(self, quoter: Prioritizer, shared_state: SharedState):
        super().__init__(quoter, shared_state)
        self._cnt = 1

    def on_orderbook_update(self) -> None:
        print("Orderbook update", self._cnt, time.time())
        #self._quoter.place_limit(ticker="A", volume=1, price=self._cnt, is_bid=True)
        self._cnt += 1

    def on_portfolio_update(self) -> None:
        print("Portfolio update")
        pass

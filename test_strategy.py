from __future__ import annotations

from src.prioritizer import Prioritizer
from src.shared_state import SharedState
from strategy import Strategy


class TestStrategy(Strategy):
    def __init__(self, quoter: Prioritizer, shared_state: SharedState):
        super().__init__(quoter, shared_state)
        self._cnt = 1

    def on_orderbook_update(self) -> None:
        print("Orderbook update")
        print(self._shared_state.orderbook.raw_orderbooks["A"]["bids"])
        print(self._shared_state.orderbook.raw_orderbooks["A"]["asks"])
        print(self._shared_state.orderbook.best_bid(ticker="A"))
        print(self._shared_state.orderbook.best_ask(ticker="A"))
        self._quoter.place_limit(ticker="A", volume=1, price=self._cnt, is_bid=True)
        self._quoter.place_limit(
            ticker="A", volume=1, price=100 - self._cnt, is_bid=False
        )
        self._cnt += 1

    def on_portfolio_update(self) -> None:
        print("Portfolio update")
        print(self._shared_state.portfolio.orders)
        pass

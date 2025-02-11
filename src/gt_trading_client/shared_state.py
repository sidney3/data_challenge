from __future__ import annotations

from .raw_orderbook import OrderBook
from .user_portfolio import UserPortfolio


class SharedState:
    def __init__(self, orderbook: OrderBook, portfolio: UserPortfolio):
        self._orderbook = orderbook
        self._portfolio = portfolio

    @property
    def orderbook(self) -> OrderBook:
        return self._orderbook

    @property
    def portfolio(self) -> UserPortfolio:
        return self._portfolio

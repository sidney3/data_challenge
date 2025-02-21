from __future__ import annotations

from .raw_orderbook import OrderBook
from .user_portfolio import UserPortfolio


class SharedState:
    """
    Shared state object to share orderbook, portfolio data across modules.
    """
    def __init__(self, orderbook: OrderBook, portfolio: UserPortfolio):
        """
        Constructor.
        Args:
            orderbook: OrderBook - reference to OrderBook object
            portfolio: UserPortfolio - reference to UserPortfolio object
        """
        self._orderbook = orderbook
        self._portfolio = portfolio

    @property
    def orderbook(self) -> OrderBook:
        """
        Getter method for orderbook
        Returns: OrderBook

        """
        return self._orderbook

    @property
    def portfolio(self) -> UserPortfolio:
        """
        Getter method for portfolio
        Returns: UserPortfolio

        """
        return self._portfolio

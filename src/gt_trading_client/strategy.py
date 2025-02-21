from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .shared_state import SharedState
    from .prioritizer import Prioritizer

from abc import ABC
from abc import abstractmethod

from sortedcontainers import SortedDict

from .config.order import Order


class Strategy(ABC):
    """
    Strategy Abstract Base Class. This class defines what constitutes a strategy.
    Has 2 abstract methods, implementations for which need to be provided:
        on_orderbook_update()
        on_portfolio_update()
    """

    def __init__(self, quoter: Prioritizer, shared_state: SharedState):
        """
        Constructor. Each strategy contains a quoter and a shared state.
        Args:
            quoter: Prioritizer - prioritizer object used for enforcing rate limits
            shared_state: SharedState - object used to represent global orderbook and user portfolio
        """
        self._quoter = quoter
        self._shared_state = shared_state

    # -------- USER PORTFOLIO METHODS --------
    def get_positions(self) -> dict[str, float]:
        """
        Getter method for positions.
        Returns: dict[str, float] - positions; dictionary with tickers as keys and volume held (position) as values

        """
        return self._shared_state.portfolio.positions

    def get_orders(self) -> dict[str, list[Order]]:
        """
        Getter method for open orders.
        Returns: dict[str, list[Order]] - orders represented as a dict with tickers as keys and Order objects as values

        """
        return self._shared_state.portfolio.orders

    def get_balance(self) -> float:
        """
        Getter method for balance.
        Returns: float - current user balance

        """
        return self._shared_state.portfolio.balance

    def get_pnl(self) -> float:
        """
        Getter method for PnL.
        Returns: float - current user PnL

        """
        return self._shared_state.portfolio.pnl

    # -------- ORDERBOOK METHODS --------
    def get_orderbooks(self) -> dict[str, dict[str, SortedDict[float, float]]]:
        """
        Gets internal orderbook representation.
        ```
        orderbook = {
            ticker1: {
                "bids": sortedcontainers.SortedDict({price1: volume1, price2: volume2,...}, reverse=True),
                "asks": sortedcontainers.SortedDict({{price1: volume1, price2: volume2,...}})
            },
            ticker2: {
                "bids": sortedcontainers.SortedDict({price1: volume1, price2: volume2,...}, reverse=True),
                "asks": sortedcontainers.SortedDict({{price1: volume1, price2: volume2,...}})
            },
            ...
        }
        ```

        Returns: dict[str, dict[str, SortedDict[float, float]]] - internal orderbook representation

        """
        return self._shared_state.orderbook.raw_orderbooks

    def get_orderbook_str(self) -> str:
        """
        Returns a string representation for orderbook (for printing purposes).

        Returns: str - string representation of orderbook

        """
        return str(self._shared_state.orderbook)

    def best_bid(self, ticker: str) -> tuple[float, float] | None:
        """
        Returns the best bid for the specified ticker in the orderbook. Returns None if there is no bid.
        Args:
            ticker: str - ticker for which the best bid is desired

        Returns: tuple[float, float] | None - tuple of price and volume of best bid

        """
        return self._shared_state.orderbook.best_bid(ticker=ticker)

    def best_ask(self, ticker: str) -> tuple[float, float] | None:
        """
        Returns the best ask for the specified ticker in the orderbook. Returns None if there is no ask.
        Args:
            ticker: str - ticker for which the bets ask is desired

        Returns: tuple[float, float] | None - tuple of price and volume of best ask

        """
        return self._shared_state.orderbook.best_ask(ticker=ticker)

    def mid(self, ticker: str) -> float | None:
        """
        Returns average of best bid and best ask for specified ticker. None if there are 0 bids or 0 asks.
        Args:
            ticker: str - ticker for which mid-price is desired

        Returns: float | None - average of best bid and best ask for specified ticker

        """
        return self._shared_state.orderbook.mid(ticker=ticker)

    def wmid(self, ticker: str) -> float | None:
        """
        Returns weighted mid-price of specified ticker. None if there are 0 bids or 0 asks.
        Args:
            ticker: str - ticker for which weighted mid-price is desired.

        Returns: float | None - mid-price of specified ticker

        """
        return self._shared_state.orderbook.wmid(ticker=ticker)

    def spread(self, ticker: str) -> float | None:
        """
        Returns spread of specified ticker. None if there are 0 bids or 0 asks.
        Args:
            ticker: str - ticker for which spread is desired

        Returns: float | None - spread of desired ticker

        """
        return self._shared_state.orderbook.spread(ticker=ticker)

    async def start(self) -> None:
        await self._quoter.subscribe()

    # -------- ABSTRACT METHODS --------
    @abstractmethod
    async def on_orderbook_update(self) -> None:
        pass

    @abstractmethod
    async def on_portfolio_update(self) -> None:
        pass

from __future__ import annotations

import copy

from sortedcontainers import SortedDict

from .config.order import Order
from .config.order import OrderSide
from .raw_orderbook import OrderBook


class FilteredOrderBook(OrderBook):
    """
    FilteredOrderBook class for representing a filtered orderbook without any of the user's open orders.
    """
    def __init__(
        self, raw_order_book: dict[str, dict[str, dict[str, str]]] | None = None
    ) -> None:
        self._orderbook = OrderBook(raw_order_book=raw_order_book)
        self._orderbooks = self._orderbook.orderbooks

    @property
    def orderbooks(self) -> dict[str, dict[str, SortedDict[float, float]]]:
        return self._orderbooks

    @property
    def raw_orderbooks(self) -> dict[str, dict[str, SortedDict[float, float]]]:
        return self._orderbook.orderbooks

    def update_volumes(
        self, updates: list[dict[str, str]], orders: dict[str, list[Order]]
    ) -> None:
        """
        Updates the orderbook with new data, filtering out all current open orders.
        Args:
            updates: list[dict[str, str]] - data structure representing updates made to orderbook
            orders: dict[str, list[Order]] - open orders of client to filter out of orderbook

        Returns: None

        """
        self._orderbook.update_volumes(updates=updates, orders=orders)
        self._orderbooks = copy.deepcopy(self._orderbook.orderbooks)
        for order_list_per_ticker in orders.values():
            for order in order_list_per_ticker:
                if order.ticker in self._orderbooks:
                    if order.side == OrderSide.BID:
                        if order.price not in self._orderbooks[order.ticker]["bids"]:
                            continue
                        self._orderbooks[order.ticker]["bids"][
                            order.price
                        ] -= order.volume
                        if self._orderbooks[order.ticker]["bids"][order.price] == 0:
                            self._orderbooks[order.ticker]["bids"].pop(
                                order.price, None
                            )
                    else:
                        if order.price not in self._orderbooks[order.ticker]["asks"]:
                            continue
                        self._orderbooks[order.ticker]["asks"][
                            order.price
                        ] -= order.volume
                        if self._orderbooks[order.ticker]["asks"][order.price] == 0:
                            self._orderbooks[order.ticker]["asks"].pop(
                                order.price, None
                            )

    def __repr__(self) -> str:
        return f"FilteredOrderBook({self._orderbooks})"

    def __str__(self) -> str:
        return super().__str__()

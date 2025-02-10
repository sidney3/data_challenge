from __future__ import annotations

import copy

from src.raw_orderbook import OrderBook
from src.config.order import Order, OrderSide


class FilteredOrderBook(OrderBook):
    def __init__(self, raw_order_book: dict | None = None):
        self._orderbook = OrderBook(raw_order_book=raw_order_book)
        self._orderbooks = self._orderbook.orderbooks

    @property
    def orderbooks(self) -> dict:
        return self._orderbooks

    @property
    def raw_orderbooks(self) -> dict:
        return self._orderbook.orderbooks

    def update_volumes(self, updates: list, orders: dict[str, list[Order]]) -> None:
        self._orderbook.update_volumes(updates=updates, orders=orders)
        self._orderbooks = copy.deepcopy(self._orderbook.orderbooks)
        for order_list_per_ticker in orders.values():
            for order in order_list_per_ticker:
                if order.ticker in self._orderbooks:
                    if order.side == OrderSide.BID:
                        self._orderbooks[order.ticker]["bids"][order.price] -= order.volume
                        if self._orderbooks[order.ticker]["bids"][order.price] == 0:
                            self._orderbooks[order.ticker]["bids"].pop(order.price, None)
                    else:
                        self._orderbooks[order.ticker]["asks"][order.price] -= order.volume
                        if self._orderbooks[order.ticker]["asks"][order.price] == 0:
                            self._orderbooks[order.ticker]["asks"].pop(order.price, None)

    def __repr__(self):
        return f"FilteredOrderBook({self._orderbooks})"

    def __str__(self):
        return super().__str__()

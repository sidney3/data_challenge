from __future__ import annotations

from typing import Any

from .config.order import Order


class UserPortfolio:
    def __init__(self) -> None:
        self._balance: float = 0
        self._pnl: float = 0
        self._positions: dict[str, dict[str, float]] = {}
        self._username = None
        self._orders: dict[str, list[Order]] = {}

    def update_portfolio(self, message: dict[str, Any]) -> None:
        if not isinstance(message, dict):
            print("Invalid message format:", message)
            return

        self._balance = float(message.get("balance", 0))
        self._pnl = float(message.get("pnl", 0))
        self._positions = message.get("positions", {})
        self._username = message.get("username")
        self._orders = {}

        orders = message.get("Orders")
        if isinstance(orders, dict):
            for ticker, order_list_per_ticker in orders.items():
                self._orders[ticker] = []
                for order in order_list_per_ticker:
                    order_with_ticker = Order(
                        ticker=ticker,
                        volume=order["volume"],
                        price=order["price"],
                        side=order["side"],
                        id=order["orderId"],
                    )
                    self._orders[ticker].append(order_with_ticker)

    def add_order(self, order: Order) -> None:
        if order.ticker not in self._orders:
            self._orders[order.ticker] = []
        self._orders[order.ticker].append(order)

    def add_position(self, ticker: str, position_delta: float, price: float) -> None:
        if ticker not in self._positions:
            self._positions[ticker] = {"quantity": 0, "averagePrice": 0}
        self._positions[ticker]["averagePrice"] *= self._positions[ticker]["quantity"]
        self._positions[ticker]["averagePrice"] += position_delta * price
        self._positions[ticker]["quantity"] += position_delta
        if self._positions[ticker]["quantity"] == 0:
            self._positions[ticker]["averagePrice"] = 0
        else:
            self._positions[ticker]["averagePrice"] /= self._positions[ticker]["quantity"]

    def clear_orders(self) -> None:
        self._orders = {}

    @property
    def positions(self) -> dict[str, float]:
        return self._positions

    @property
    def orders(self) -> dict[str, list[Order]]:
        return self._orders

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def pnl(self) -> float:
        return self._pnl

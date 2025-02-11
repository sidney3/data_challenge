from __future__ import annotations

from typing import Any

from .config.order import Order


class UserPortfolio:
    def __init__(self) -> None:
        self._balance: float = 0
        self._pnl: float = 0
        self._positions: dict[str, float] = {}
        self._username = None
        self._orders: dict[str, list[Order]] = {}

    # Replace the entire portfolio data with a new message
    def update_portfolio(self, message: dict[str, Any]) -> None:
        if not isinstance(message, dict):
            print("Invalid message format:", message)
            return

        # Reset the portfolio and set it to the new message
        self._balance = float(message.get("balance", 0))
        self._pnl = float(message.get("pnl", 0))
        self._positions = message.get("positions", {})  # Replaces completely
        self._username = message.get("username")
        self._orders = {}

        # Process orders if provided
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

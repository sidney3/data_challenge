from __future__ import annotations

from sortedcontainers import SortedDict
from src.config.order import Order


class OrderBook:
    def __init__(self, raw_order_book: dict | None = None):
        if raw_order_book is None:
            raw_order_book = {}
        if not isinstance(raw_order_book, dict):
            raise TypeError("Input data must be a dictionary.")

        self._orderbooks: dict[str, dict[str, SortedDict[float, float]]] = {}
        for ticker, volumes in raw_order_book.items():
            self._orderbooks[ticker] = {
                "bids": self._create_sorted_dict(
                    volumes.get("bidVolumes", {}), reverse=True
                ),
                "asks": self._create_sorted_dict(
                    volumes.get("askVolumes", {}), reverse=False
                ),
            }

    @property
    def orderbooks(self) -> dict:
        return self._orderbooks
    
    @property
    def best_bid(self, ticker: str) -> tuple[float, float]:
        best_bid = self._orderbooks[ticker]["bids"].peekitem(index=0)
        return best_bid

    @property
    def best_ask(self, ticker: str) -> tuple[float, float]:
        best_ask = self._orderbooks[ticker]["asks"].peekitem(index=0)
        return best_ask
    
    @property
    def mid(self) -> float:
        return (self.best_bid[0] + self.best_ask[0]) / 2

    @property
    def wmid(self) -> float:
        best_bid = self.best_bid
        best_ask = self.best_ask
        return (best_bid[0] * best_ask[1] + best_ask[0] * best_bid[1]) / (best_bid[1] + best_ask[1])
    
    @property
    def spread(self) -> float:
        return self.best_ask[0] - self.best_bid[0]

    def _create_sorted_dict(
        self, volumes: dict, reverse: bool
    ) -> SortedDict[float, float]:
        if reverse:
            return SortedDict(
                lambda x: -x,
                [
                    (float(price), float(qty)) for price, qty in volumes.items()
                ]
            )
        else:
            return SortedDict(
                [
                    (float(price), float(qty)) for price, qty in volumes.items()
                ]
            )

    def update_volumes(self, updates: list, orders: dict[str, list[Order]]) -> None:
        if not isinstance(updates, list):
            raise TypeError("Updates must be provided as a list.")

        for update in updates:
            if (
                not isinstance(update, dict)
                or "ticker" not in update
                or "price" not in update
                or "side" not in update
                or "volume" not in update
            ):
                raise ValueError(
                    "Each update must be a dictionary with keys 'ticker', 'price', 'side', and 'volume'."
                )

            ticker = update["ticker"]
            price = float(update["price"])
            side = update["side"].upper()
            volume = float(update["volume"])

            if ticker not in self._orderbooks:
                self._orderbooks[ticker] = {
                    "bids": SortedDict(lambda x: -x),
                    "asks": SortedDict(),
                }

            if side == "BID":
                if volume == 0.0:
                    self._orderbooks[ticker]["bids"].pop(price, None)
                else:
                    self._orderbooks[ticker]["bids"][price] = volume
                    self._orderbooks[ticker]["bids"] = self._create_sorted_dict(
                        self._orderbooks[ticker]["bids"], reverse=True
                    )
            elif side == "ASK":
                if volume == 0.0:
                    self._orderbooks[ticker]["asks"].pop(price, None)
                else:
                    self._orderbooks[ticker]["asks"][price] = volume
                    self._orderbooks[ticker]["asks"] = self._create_sorted_dict(
                        self._orderbooks[ticker]["asks"], reverse=False
                    )
            else:
                raise ValueError("Side must be 'BID' or 'ASK'.")

    def __repr__(self):
        return f"OrderBook({self._orderbooks})"

    def __str__(self):
        output = []
        for ticker, data in self._orderbooks.items():
            output.append(f"Ticker: {ticker}")
            output.append("  Bid Volumes:")
            for price, volume in data["bids"].items():
                output.append(f"    {price:.2f}: {volume:.2f}")
            output.append("  Ask Volumes:")
            for price, volume in data["asks"].items():
                output.append(f"    {price:.2f}: {volume:.2f}")
        return "\n".join(output)

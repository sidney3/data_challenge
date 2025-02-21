from __future__ import annotations

from sortedcontainers import SortedDict

from .config.order import Order


class OrderBook:
    """
    OrderBook class for representing orders in orderbook.
    """
    def __init__(
        self, raw_order_book: dict[str, dict[str, dict[str, str]]] | None = None
    ):
        """
        Constructor. Initializes OrderBook state with raw order book.

        Creates orderbook representation:
            orderbook = {
                ticker1: {
                    "bids": SortedDict({price1: volume1, price2: volume2,...}, reverse=True),
                    "asks": SortedDict({{price1: volume1, price2: volume2,...}})
                },
                ticker2: {
                    "bids": SortedDict({price1: volume1, price2: volume2,...}, reverse=True),
                    "asks": SortedDict({{price1: volume1, price2: volume2,...}})
                },
                ...
            }

        Args:
            raw_order_book: dict[str, dict[str, dict[str, str]]] - representation of a raw orderbook;
                - layer1 (orderbook): maps tickers [str] to volumes [dict]
                - layer2 (volumes): maps bidVolumes or askVolumes to prices/volumes
        """
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
    def orderbooks(self) -> dict[str, dict[str, SortedDict[float, float]]]:
        """
        Gets internal orderbook representation

        Returns: dict[str, dict[str, SortedDict[float, float]]] - internal orderbook representation

        """
        return self._orderbooks

    @property
    def raw_orderbooks(self) -> dict[str, dict[str, SortedDict[float, float]]]:
        """
        Gets internal orderbook representation

        Returns: dict[str, dict[str, SortedDict[float, float]]] - internal orderbook representation

        """
        return self._orderbooks

    def best_bid(self, ticker: str) -> tuple[float, float] | None:
        """
        Returns the best bid for the specified ticker in the orderbook. Returns None if there is no bid.
        Args:
            ticker: str - ticker for which the best bid is desired

        Returns: tuple[float, float] | None - tuple of price and volume of best bid

        """
        if self._orderbooks[ticker]["bids"]:
            return self._orderbooks[ticker]["bids"].peekitem(index=0)
        return None

    def best_ask(self, ticker: str) -> tuple[float, float] | None:
        """
        Returns the best ask for the specified ticker in the orderbook. Returns None if there is no ask.
        Args:
            ticker: str - ticker for which the bets ask is desired

        Returns: tuple[float, float] | None - tuple of price and volume of best ask

        """
        if self._orderbooks[ticker]["asks"]:
            return self._orderbooks[ticker]["asks"].peekitem(index=0)
        return None

    def mid(self, ticker: str) -> float | None:
        """
        Returns average of best bid and best ask for specified ticker. None if there are 0 bids or 0 asks.
        Args:
            ticker: str - ticker for which mid-price is desired

        Returns: float | None - average of best bid and best ask for specified ticker

        """
        best_bid = self.best_bid(ticker=ticker)
        best_ask = self.best_ask(ticker=ticker)
        if best_bid is None or best_ask is None:
            return None
        return (best_bid[0] + best_ask[0]) / 2

    def wmid(self, ticker: str) -> float | None:
        """
        Returns weighted mid-price of specified ticker. None if there are 0 bids or 0 asks.
        Args:
            ticker: str - ticker for which weighted mid-price is desired.

        Returns: float | None - mid-price of specified ticker

        """
        best_bid = self.best_bid(ticker=ticker)
        best_ask = self.best_ask(ticker=ticker)
        if best_bid is None or best_ask is None:
            return None
        return (best_bid[0] * best_ask[1] + best_ask[0] * best_bid[1]) / (
            best_bid[1] + best_ask[1]
        )

    def spread(self, ticker: str) -> float | None:
        """
        Returns spread of specified ticker. None if there are 0 bids or 0 asks.
        Args:
            ticker: str - ticker for which spread is desired

        Returns: float | None - spread of desired ticker

        """
        best_bid = self.best_bid(ticker=ticker)
        best_ask = self.best_ask(ticker=ticker)
        if best_bid is None or best_ask is None:
            return None
        return best_ask[0] - best_bid[0]

    def _create_sorted_dict(
        self, volumes: dict[str, str], reverse: bool
    ) -> SortedDict[float, float]:
        """
        Helper method for creating a sorted dictionary, given dictionary.

        Args:
            volumes: dict - dictionary representing raw volumes
            reverse: bool - indicates if SortedDict should be in reverse order

        Returns: SortedDict - sorted dictionary representation of dict

        """
        if reverse:
            return SortedDict(
                lambda x: -x,
                [(float(price), float(qty)) for price, qty in volumes.items()],
            )
        else:
            return SortedDict(
                [(float(price), float(qty)) for price, qty in volumes.items()]
            )

    def update_volumes(
        self, updates: list[dict[str, str]], orders: dict[str, list[Order]]
    ) -> None:
        """
        Updates the orderbook with new data.
        Args:
            updates: list[dict[str, str]] - data structure representing updates made to orderbook
            orders: dict[str, list[Order]]

        Returns: None

        """
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
                    "bids": self._create_sorted_dict({}, reverse=True),
                    "asks": self._create_sorted_dict({}, reverse=False),
                }

            if side == "BID":
                if volume == 0.0:
                    self._orderbooks[ticker]["bids"].pop(price, None)
                else:
                    self._orderbooks[ticker]["bids"][price] = volume
            elif side == "ASK":
                if volume == 0.0:
                    self._orderbooks[ticker]["asks"].pop(price, None)
                else:
                    self._orderbooks[ticker]["asks"][price] = volume
            else:
                raise ValueError("Side must be 'BID' or 'ASK'.")

    def __repr__(self) -> str:
        """
        Overrides __repr__ magic method.

        Returns: str - object's string representation

        """
        return f"OrderBook({self._orderbooks})"

    def __str__(self) -> str:
        """
        Overrides __str__ magic method.

        Returns: str - object's string representation

        """
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

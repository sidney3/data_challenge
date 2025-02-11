from __future__ import annotations

import json
import urllib.request

from .filtered_orderbook import FilteredOrderBook
from .raw_orderbook import OrderBook
from .shared_state import SharedState
from .user_portfolio import UserPortfolio
from .websocket_client import WebSocketClient
from .strategy import Strategy


class TradingClient:
    def __init__(
        self, http_endpoint: str, ws_endpoint: str, username: str, api_key: str
    ):
        self._http_endpoint = http_endpoint
        self._ws_endpoint = ws_endpoint
        self._username = username
        self._api_key = api_key
        self._strategy = None

        self._user_buildup()

    def set_strategy(self, strategy: Strategy) -> None:
        self._client.set_strategy(strategy)

    def _user_buildup(self) -> None:
        """Authenticate the user and obtain a session token."""
        form_data = {"username": self._username, "apiKey": self._api_key}
        req = urllib.request.Request(
            self._http_endpoint + "/buildup",
            data=json.dumps(form_data).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        response = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
        self._session_token = response.get("sessionToken")
        self._orderbook: OrderBook = FilteredOrderBook(
            raw_order_book=json.loads(response["orderBookData"])
        )
        self._user_portfolio = UserPortfolio()
        self._client = WebSocketClient(
            endpoint=self._ws_endpoint,
            orderbook=self._orderbook,
            session_token=self._session_token,
            portfolio=self._user_portfolio,
            username=self._username,
        )
        self._shared_state = SharedState(
            orderbook=self._orderbook,
            portfolio=self._user_portfolio,
        )

    @property
    def shared_state(self) -> SharedState:
        return self._shared_state

    def place_limit(
        self, ticker: str, volume: float, price: float, is_bid: bool
    ) -> None:
        """Place a Limit Order on the exchange."""
        if not self._session_token:
            raise Exception("User not authenticated. Call user_buildup first.")

        form_data = {
            "username": self._username,
            "sessionToken": self._session_token,
            "ticker": ticker,
            "volume": volume,
            "price": price,
            "isBid": is_bid,
        }
        req = urllib.request.Request(
            self._http_endpoint + "/limit_order",
            data=json.dumps(form_data).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        content = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))

    def place_market(self, ticker: str, volume: float, is_bid: bool) -> None:
        """Place a Market Order on the exchange."""
        if not self._session_token:
            raise Exception("User not authenticated. Call user_buildup first.")

        form_data = {
            "username": self._username,
            "sessionToken": self._session_token,
            "ticker": ticker,
            "volume": volume,
            "isBid": is_bid,
        }
        req = urllib.request.Request(
            self._http_endpoint + "/market_order",
            data=json.dumps(form_data).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        content = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))

    def remove_all(
        self,
    ) -> None:
        form_data = {
            "username": self._username,
            "sessionToken": self._session_token,
        }
        req = urllib.request.Request(
            self._http_endpoint + "/remove_all",
            data=json.dumps(form_data).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        response = urllib.request.urlopen(req).read().decode("utf-8")

    def get_details(self) -> None:
        form_data = {
            "username": self._username,
            "sessionToken": self._session_token,
        }
        req = urllib.request.Request(
            self._http_endpoint + "/get_details",
            data=json.dumps(form_data).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        response = urllib.request.urlopen(req).read().decode("utf-8")

    async def subscribe(self) -> None:
        await self._client.subscribe()

    async def unsubscribe(self) -> None:
        await self._client.unsubscribe()

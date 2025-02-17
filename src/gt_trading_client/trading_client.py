from __future__ import annotations

from typing import Any

import json
import urllib.request
import aiohttp
import asyncio

from .filtered_orderbook import FilteredOrderBook
from .raw_orderbook import OrderBook
from .shared_state import SharedState
from .user_portfolio import UserPortfolio
from .websocket_client import WebSocketClient
from .strategy import Strategy
from .config.order import Order, OrderSide


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
    
    def _error_check(self, message: dict[str, Any]) -> bool:
        if message["error"] != "":
            return False
        return True

    def _limit_params(self, ticker: str, volume: float, price: float, is_bid: bool) -> tuple[str, dict[str, Any]]:
        url = f"{self._http_endpoint}/limit_order"
        form_data = {
            "username": self._username,
            "sessionToken": self._session_token,
            "ticker": ticker,
            "volume": volume,
            "price": price,
            "isBid": is_bid,
        }
        return (url, form_data)

    async def place_limit(self, ticker: str, volume: float, price: float, is_bid: bool) -> None:
        """ Sends a limit order asynchronously using aiohttp """
        if not self._session_token:
            raise Exception("User not authenticated. Call user_buildup first.")

        url, form_data = self._limit_params(ticker=ticker, volume=volume, price=price, is_bid=is_bid)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=form_data) as response:
                content = await response.json()
                message = json.loads(content["message"])
                if not self._error_check(message=message):
                    return
                volume_filled = message["volumeFilled"]
                volume_remaining = volume - volume_filled
                order_id = message["orderId"]
                if volume_filled > 0:
                    self._user_portfolio.add_position(
                        ticker=ticker,
                        position_delta=volume_filled if is_bid else -volume_filled,
                    )
                if volume_remaining > 0:
                    self._user_portfolio.add_order(
                        order=Order(
                            ticker=ticker,
                            volume=volume_remaining,
                            price=price,
                            side=OrderSide.BID if is_bid else OrderSide.ASK,
                            id=order_id,
                        )
                    )

    def _market_params(self, ticker: str, volume: float, price: float, is_bid: bool) -> tuple[str, dict[str, Any]]:
        url = f"{self._http_endpoint}/market_order"
        form_data = {
            "username": self._username,
            "sessionToken": self._session_token,
            "ticker": ticker,
            "volume": volume,
            "isBid": is_bid,
        }
        return (url, form_data)

    async def place_market(self, ticker: str, volume: float, is_bid: bool) -> None:
        """Place a market order asynchronously using aiohttp."""
        if not self._session_token:
            raise Exception("User not authenticated. Call user_buildup first.")

        url, form_data = self._market_params(ticker=ticker, volume=volume, is_bid=is_bid)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=form_data) as response:
                content = await response.json()
                message = json.loads(content["message"])

                if not self._error_check(message=message):
                    return

                volume_filled = message["volumeFilled"]
                if volume_filled > 0:
                    self._user_portfolio.add_position(
                        ticker=ticker,
                        position_delta=volume_filled if is_bid else -volume_filled,
                    )

    def _remove_all_params(self) -> tuple[str, dict[str, Any]]:
        url = f"{self._http_endpoint}/remove_all"
        form_data = {
            "username": self._username,
            "sessionToken": self._session_token,
        }
        return (url, form_data)

    async def remove_all(self) -> None:
        """Remove all orders asynchronously using aiohttp."""
        if not self._session_token:
            raise Exception("User not authenticated. Call user_buildup first.")

        url, form_data = self._remove_all_params()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=form_data) as response:
                content = await response.json()  # Parse JSON response asynchronously
                message = json.loads(content["message"]) if content.get("message") else None

                if not message or not self._error_check(message=message):
                    return

                self._user_portfolio.clear_orders()

    async def subscribe(self) -> None:
        await self._client.subscribe()

    async def unsubscribe(self) -> None:
        await self._client.unsubscribe()

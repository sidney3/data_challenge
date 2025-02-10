from __future__ import annotations

import asyncio
import json
import traceback

import websockets

from src.raw_orderbook import OrderBook
from src.user_portfolio import UserPortfolio
from strategy import Strategy

class WebSocketClient:
    def __init__(self, endpoint: str, orderbook: OrderBook, session_token: str, portfolio: UserPortfolio, username: str):
        self._endpoint = f"{endpoint}?Session-ID={session_token}&Username={username}"
        self._subscribed: asyncio.Event | None = None
        self._ws = None
        self._orderbook = orderbook
        self._session_token = session_token
        self._portfolio = portfolio
        self._username = username
        self._strategy: Strategy | None = None

    def set_strategy(self, strategy: Strategy):
        self._strategy = strategy 

    async def _on_open(self, ws: websockets.ClientConnection):
        print("WebSocket connection established")
        # Send STOMP CONNECT frame
        connect_frame = (
            f"CONNECT\n"
            f"accept-version:1.1,1.0\n"
            f"host:localhost\n"
            "\n\x00"
        )
        await ws.send(connect_frame)

        # Subscribe to orderbook topic
        subscribe_frame = (
            "SUBSCRIBE\n"
            "id:sub-0\n"
            "destination:/topic/orderbook\n"
            "\n\x00"
        )
        await ws.send(subscribe_frame)

        # Subscribe to private user queue
        user_subscribe_frame = (
            f"SUBSCRIBE\n"
            f"id:sub-1\n"
            f"destination:/user/queue/private\n"
            "\n\x00"
        )
        await ws.send(user_subscribe_frame)
        self._subscribed.set()
        print("STOMP connection and subscription established")

    async def _on_message(
        self, ws: websockets.ClientConnection, message: websockets.Data
    ):
        try:
            if isinstance(message, bytes):
                message = message.decode("utf-8")

            if "\n\n" in message:
                headers, body = message.split("\n\n", 1)
                body = body.replace("\x00", "").strip()
                json_body = json.loads(body)


                destination = None
                for line in headers.split("\n"):
                    if line.startswith("destination:"):
                        destination = line.split(":", 1)[1].strip()
                        break

                if destination == "/topic/orderbook":
                    if "content" in json_body:
                        content = json.loads(json_body["content"])
                        if isinstance(content, list):
                            self._orderbook.update_volumes(updates=content, orders=self._portfolio.orders)
                            if self._strategy:
                                self._strategy.on_orderbook_update()

                elif destination == "/user/queue/private":
                    if json_body and "balance" in json_body or "Orders" in json_body:
                        self._portfolio.update_portfolio(json_body)
                        if self._strategy:
                            self._strategy.on_portfolio_update()

        except Exception as e:
            print(f"Error processing message: {e}")
            traceback.print_exc()

    async def _on_error(self, ws: websockets.ClientConnection, error: Exception):
        print(f"Error: {error}")

    async def _on_close(
        self, ws: websockets.ClientConnection, close_status_code: int, close_msg: str
    ):
        print(f"Disconnected: {close_msg if close_msg else 'No message'}")
        self._connected = False

    async def _subscribe_ws(self):
        while True:
            try:
                async with websockets.connect(self._endpoint) as ws:
                    await self._on_open(ws)
                    self._ws = ws
                    while True:
                        try:
                            message = await ws.recv()
                            await self._on_message(ws, message)
                        except websockets.ConnectionClosed as e:
                            await self._on_close(ws, e.code, e.reason)
                            break
            except Exception as e:
                await self._on_error(None, e)
                await asyncio.sleep(5)

    async def subscribe(self):
        if self._subscribed:
            await self._subscribed.wait()
        self._subscribed = asyncio.Event()
        self._task = asyncio.create_task(self._subscribe_ws())
        await self._subscribed.wait()

    async def unsubscribe(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._ws:
            await self._ws.close()
            self._ws = None
        self._subscribed = None

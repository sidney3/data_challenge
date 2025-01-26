from __future__ import annotations

import asyncio
import json
import time
import traceback

import websockets

from src.orderbook import OrderBook


class WebSocketClient:
    def __init__(self, endpoint: str, orderbook: OrderBook):
        self._endpoint = endpoint
        self._subscribed: asyncio.Event | None = None
        self._ws = None
        self._orderbook = orderbook

    async def _on_open(self, ws: websockets.ClientConnection):
        print("WebSocket connection established")
        # Send STOMP CONNECT frame
        connect_frame = "CONNECT\naccept-version:1.1,1.0\nhost:localhost\n\n\x00"
        await ws.send(connect_frame)

        # Subscribe to orderbook topic
        subscribe_frame = (
            "SUBSCRIBE\nid:sub-0\ndestination:/topic/orderbook\nack:auto\n\n\x00"
        )
        await ws.send(subscribe_frame)

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

                if "content" in json_body:
                    content = json.loads(json_body["content"])
                    if isinstance(content, list):
                        self._orderbook.update_volumes(content)
                    print("Timestamp:", time.time())
                    print(self._orderbook)
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

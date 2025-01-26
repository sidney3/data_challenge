from __future__ import annotations

import asyncio
import traceback

import uvloop

from src.trading_client import TradingClient

API_KEY = "XPVLFSMBZVYHNDWG"
username = "team99"
URL = "http://ec2-13-59-143-196.us-east-2.compute.amazonaws.com:8080"
WS_URL = "ws://ec2-13-59-143-196.us-east-2.compute.amazonaws.com:8080/exchange-socket"


async def start_strategy():
    client = TradingClient(
        http_endpoint=URL,
        ws_endpoint=WS_URL,
        username=username,
        api_key=API_KEY,
    )

    await client.subscribe()

    while True:
        await asyncio.sleep(1)


async def main():
    tasks = [asyncio.create_task(start_strategy())]
    try:
        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )
        print(results)
    except Exception as e:
        traceback.print_exc()
        for task in tasks:
            task.cancel()
        await asyncio.gather(tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())

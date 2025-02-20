from __future__ import annotations

import asyncio
import traceback

from gt_trading_client import Prioritizer
from gt_trading_client import TradingClient
from gt_trading_client import Strategy
from test_strategy import TestStrategy

RATE_LIMIT = 15
API_KEY = "PMNFAPQYDFPDAAGS"
USERNAME = "team97"
URL = "http://ec2-3-16-107-184.us-east-2.compute.amazonaws.com:8080"
WS_URL = "ws://ec2-3-16-107-184.us-east-2.compute.amazonaws.com:8080/exchange-socket"


async def start_strategy() -> None:
    client = TradingClient(
        http_endpoint=URL,
        ws_endpoint=WS_URL,
        username=USERNAME,
        api_key=API_KEY,
    )
    shared_state = client.shared_state
    prioritizer = Prioritizer(rate_limit=RATE_LIMIT, trading_client=client)

    strategy: Strategy = TestStrategy(quoter=prioritizer, shared_state=shared_state)

    client.set_strategy(strategy=strategy)

    await strategy.start()

    await asyncio.sleep(1000000)


async def main() -> None:
    tasks: list[asyncio.Task[None]] = [asyncio.create_task(start_strategy())]
    try:
        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )
        print(results)
    except Exception as e:
        print("Exception in main", e)
        traceback.print_exc()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())

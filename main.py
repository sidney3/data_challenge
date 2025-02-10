from __future__ import annotations

import asyncio
import traceback

import uvloop

from src.trading_client import TradingClient
from src.prioritizer import Prioritizer
from strategy import Strategy
from test_strategy import TestStrategy
from data_challenge_strategy import DataChallengeStrategy

RATE_LIMIT = 5
API_KEY = "PMNFAPQYDFPDAAGS"
username = "team97"
URL = "http://ec2-3-16-107-184.us-east-2.compute.amazonaws.com:8080"
WS_URL = "ws://ec2-3-16-107-184.us-east-2.compute.amazonaws.com:8080/exchange-socket"


async def start_strategy():
    client = TradingClient(
        http_endpoint=URL,
        ws_endpoint=WS_URL,
        username=username,
        api_key=API_KEY,
    )
    shared_state = client.shared_state
    prioritizer = Prioritizer(rate_limit=RATE_LIMIT, trading_client=client)

    strat: Strategy = DataChallengeStrategy(quoter=prioritizer, shared_state=shared_state)

    client.set_strategy(strategy=strat)
    
    await strat.start()

    await asyncio.sleep(10)

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

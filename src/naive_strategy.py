from __future__ import annotations

from gt_trading_client import Prioritizer
from gt_trading_client import SharedState
from gt_trading_client import Strategy

from config import Config
from pricing_engine import PricingEngine, FairValue

import pandas as pd
import numpy as np
import time
from datetime import datetime,timedelta
import asyncio

def time_delta_to_seconds(td: timedelta) -> float:
    return (td / timedelta(seconds=1))

class NaiveStrategy(Strategy):
    pricing_engine_: PricingEngine
    config_: Config

    def __init__(self, quoter: Prioritizer, shared_state: SharedState, config: Config, historical_data: pd.DataFrame):
        super().__init__(quoter, shared_state)
        self.pricing_engine_ = PricingEngine(shared_state, historical_data, config)
        self.config_ = config
        self.last_time_we_traded_ = datetime.now()
        self.last_quoted_at_ = pd.Series({ticker: FairValue(0,0) for ticker in self.config_.tickers})

    # should we pull ALL of our orders? Check if any fair values fall far outside
    # our posted ranges. We will act on this instantly (i.e. ignoring rate limits)
    # so this should be rare-ish
    def we_should_pull_our_orders(self, fair_values) -> bool:
        orders = self.get_orders()
        for ticker in self.config_.tickers:
            for order in orders[ticker]:
                if fair_values[ticker].distance_outside_sdevs(order.price, 2) >= self.config_.close_position_if_this_far_outside:
                    return True
        return False

    async def place_limit_by_fair_value(self, fair_value, ticker, quantity, sdevs):
        lower_bound = fair_value.price - sdevs * fair_value.sdev
        upper_bound = fair_value.price + sdevs * fair_value.sdev

        asyncio.create_task(self._quoter.place_limit(ticker=ticker, volume=quantity, price=lower_bound, is_bid = True))
        asyncio.create_task(self._quoter.place_limit(ticker=ticker, volume=quantity, price=upper_bound, is_bid = False))

    async def place_junk_orders(self):
        print(f'placing junk orders')
        await self._quoter.remove_all()
        fair_values = self.pricing_engine_.fair_values()
        for ticker in self.config_.tickers:
            asyncio.create_task(self.place_limit_by_fair_value(fair_value=fair_values[ticker], ticker=ticker, quantity=1, sdevs = 10))
            asyncio.create_task(self.place_limit_by_fair_value(fair_value=fair_values[ticker], ticker=ticker, quantity=1, sdevs = 20))

    async def do_every(self, td: timedelta, fn) -> None:
        print("do every body")
        while True:
            await fn()
            await asyncio.sleep(td / timedelta(seconds=1))

    async def periodic_jobs(self) -> None:
        print("do periodic jobs")

        place_junk_orders = asyncio.create_task(self.do_every(timedelta(seconds=10), self.place_junk_orders))

        await asyncio.gather(place_junk_orders)

    async def on_orderbook_update(self) -> None:
        # print("Orderbook update", datetime.now())
        self.pricing_engine_.on_tick()

    async def on_portfolio_update(self) -> None:
        print(f'Portfolio update. New PNL: {self.get_pnl()}')
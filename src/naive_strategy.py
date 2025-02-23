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
        return False

    # not an "urgent" method. I.E. will send a bunch of cancels at a rate that we 
    # know we won't get limited at
    async def close_stale_positions(self, fair_values) -> None:
        pass

    async def refresh_levels(self) -> None:
        """
        Based on the computed fair values, refresh all of our levels
        """
        fair_values = self.pricing_engine_.fair_values()

        if(self.we_should_pull_our_orders(fair_values=fair_values)):
            pass

        # TODO: what's the API endpoint to remove a specific order?
        should_update_levels = (datetime.now() - self.last_time_we_traded_) > self.config_.rate_limit

        if not should_update_levels:
            return

        print(f'time since we last traded: {datetime.now() - self.last_time_we_traded_}')
        self.last_time_we_traded = datetime.now()
        self.last_quoted_at_ = fair_values

        for ticker in self.config_.tickers:
            asyncio.create_task(self.close_stale_positions(ticker=ticker, fair_values=fair_values))

            sdev = np.sqrt(fair_values[ticker].variance)
            assert sdev
            lower_bound = fair_values[ticker].price - 2 * sdev
            upper_bound = fair_values[ticker].price + 2 * sdev

            asyncio.create_task(self._quoter.place_limit(ticker=ticker, volume= 50, price=lower_bound, is_bid = True))
            asyncio.create_task(self._quoter.place_limit(ticker=ticker, volume= 50, price=upper_bound, is_bid = False))



    async def on_orderbook_update(self) -> None:
        print("Orderbook update", datetime.now())
        self.pricing_engine_.on_tick()
        asyncio.create_task(self.refresh_levels())

    async def on_portfolio_update(self) -> None:
        print(f'Portfolio update. New PNL: {self.get_pnl()}')
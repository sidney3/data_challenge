from __future__ import annotations

from gt_trading_client import Prioritizer
from gt_trading_client import SharedState
from gt_trading_client import Strategy

from config import Config
from pricing_engine import PricingEngine

import pandas as pd
import numpy as np
import time
from datetime import datetime
import asyncio

class NaiveStrategy(Strategy):
    pricing_engine_: PricingEngine
    config_: Config

    def __init__(self, quoter: Prioritizer, shared_state: SharedState, config: Config, historical_data: pd.DataFrame):
        super().__init__(quoter, shared_state)
        self.pricing_engine_ = PricingEngine(shared_state, historical_data, config)
        self.config_ = config
        self.next_allowed_trade_ = datetime.now() + self.config_.trade_every

    async def on_orderbook_update(self) -> None:
        print("Orderbook update", self._cnt, time.time())
        self.notify_count_ += 1
        self.pricing_engine_.on_tick()
        if datetime.now() < self.next_allowed_trade_:
            return

        self.next_allowed_trade_ = datetime.now() + self.config_.trade_every
        fair_values, variances = self.pricing_engine_.fair_values()
        for ticker in self.config_.tickers:
            sdev = np.sqrt(variances[ticker])

            z_value = 1.645  # 90% confidence level
            lower_bound = fair_values[ticker] - z_value * sdev
            upper_bound = fair_values[ticker] + z_value * sdev

            asyncio.create_task(self._quoter.place_limit(ticker=ticker, volume = 1, price = lower_bound, is_bid = True))
            asyncio.create_task(self._quoter.place_limit(ticker=ticker, volume = 1, price = upper_bound, is_bid = False))

    async def on_portfolio_update(self) -> None:
        print(f'Portfolio update. New PNL: {self.get_pnl()}')
        print(self._shared_state.portfolio.positions)
        pass

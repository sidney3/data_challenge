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
        self.last_quoted_at_ = pd.Series([0 for _ in config.tickers], index=config.tickers)
        self.last_time_we_traded_ = datetime.now()

    async def refresh_levels(self) -> None:
        """
        Based on the computed fair values, refresh all of our levels
        """
        fair_values, variances = self.pricing_engine_.fair_values()

        max_price_discrepency = max(fair_values - self.last_quoted_at_)

        if max_price_discrepency >= self.config_.close_all_positions_limit:
            await self._quoter.remove_all()

        should_update_levels = max_price_discrepency >= self.config_.change_our_position_within \
            and (datetime.now() - self.last_time_we_traded_) > self.config_.rate_limit

        if not should_update_levels:
            return

        print(f'time since we last traded: {datetime.now() - self.last_time_we_traded_}')
        self.last_time_we_traded = datetime.now()
        self.last_quoted_at_ = fair_values

        await self._quoter.remove_all()

        for ticker in self.config_.tickers:
            sdev = np.sqrt(variances[ticker])
            print(f'{variances[ticker]=}, {sdev=}')
            z_value = 1.645  # 90% confidence level
            lower_bound = fair_values[ticker] - 2 * sdev
            upper_bound = fair_values[ticker] + 2 * sdev

            asyncio.create_task(self._quoter.place_limit(ticker=ticker, volume= 50, price=lower_bound, is_bid = True))
            asyncio.create_task(self._quoter.place_limit(ticker=ticker, volume= 50, price=upper_bound, is_bid = False))



    async def on_orderbook_update(self) -> None:
        print("Orderbook update", datetime.now())
        self.pricing_engine_.on_tick()
        asyncio.create_task(self.refresh_levels())

    async def on_portfolio_update(self) -> None:
        print(f'Portfolio update. New PNL: {self.get_pnl()}')
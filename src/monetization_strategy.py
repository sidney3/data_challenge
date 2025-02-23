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

class MonetizationStrategy(Strategy):
    pricing_engine_: PricingEngine
    config_: Config
    recent_ticks_: list[pd.Series]

    def __init__(self, quoter: Prioritizer, shared_state: SharedState, config: Config, historical_data: pd.DataFrame):
        super().__init__(quoter, shared_state)
        self.pricing_engine_ = PricingEngine(shared_state, historical_data, config)
        self.config_ = config
        self.last_time_we_traded_ = datetime.now()
        
        # for each asset, the price we expect it to rise to
        self.anticipated_price_ = pd.Series({
            ticker: None for ticker in self.config_.tickers
        })

        self.recent_ticks_ = []
        for i, row in historical_data.iterrows():
            self.recent_ticks_.append(row)

    async def try_exit_positions(self):
        positions = self.get_positions()
        for ticker in self.config_.tickers:
            if not self.anticipated_price_[ticker]:
                continue

            best_bid, bid_volume = self.best_bid(ticker)
            best_ask, ask_volume = self.best_ask(ticker)

            holding = positions[ticker]['quantity']
            # we are short. Check if the ticker is below where we expect it to be (and in this case buy to close out our position)
            if holding < 0 and self.anticipated_price_[ticker] < best_ask:
                volume_to_execute = min(ask_volume, abs(positions[ticker]))
                # Buy to close out our short position
                print(f'We should close out our position on {ticker}')
                # asyncio.create_task(self._quoter.place_market(ticker=ticker, volume=volume_to_execute, is_bid=True))
            # we are long. Check if the ticker is above where we expect it to be (and in this case sell to close out our position)
            elif holding > 0 and self.anticipated_price_[ticker] > best_bid:
                volume_to_execute = min(bid_volume, abs(positions[ticker]))
                # Sell to close out our long our position
                print(f'We should close out our position on {ticker}')
                # asyncio.create_task(self._quoter.place_market(ticker=ticker, volume=volume_to_execute, is_bid=False))
            pass

    async def enter_positions(self):
        fair_values = self.pricing_engine_.fair_values()
        positions = self.get_positions()

        for ticker in self.config_.tickers:
            best_bid, bid_volume = self.best_bid(ticker)
            best_ask, ask_volume = self.best_ask(ticker)

            price = (best_bid - best_ask) / 2

            holding = 0
            if ticker in positions:
                holding = positions[ticker]['quantity']

            # the fair value is BIGGER than ask by significant margin. So go short 
            if (fair_values[ticker].price - best_ask) > self.config_.enter_position_limit and holding > -self.config_.position_limit:
                print(f'We should enter a short position on {ticker}')
                #asyncio.create_task(self._quoter.place_market(ticker=ticker, volume=min(self.config_.position_limit, ask_volume), is_bid=False))
                pass
            # the fair value is LOWER than price by significant margin. So go long
            elif (best_bid - fair_values[ticker].price) > self.config_.enter_position_limit and holding < self.config_.position_limit:
                print(f'We should enter a long position on {ticker}')
                #asyncio.create_task(self._quoter.place_market(ticker=ticker, volume=min(self.config_.position_limit, bid_volume), is_bid=True))

    # d is sinusoidal
    async def buy_or_sell_d(self):
        best_bid, bid_volume = self.best_bid('D')
        best_ask, ask_volume = self.best_ask('D')
        positions = self.get_positions()

        holding = 0
        if 'D' in positions:
            holding = positions['D']['quantity']

        if best_ask <= 180 and holding < self.config_.position_limit:
            asyncio.create_task(self._quoter.place_market(ticker='D', volume=self.config_.position_limit, is_bid=True))
        elif best_bid >= 200 and holding > 0:
            asyncio.create_task(self._quoter.place_market(ticker='D', volume=positions['D']['quantity'], is_bid=False))

    async def buy_or_sell_c(self):
        """
        C is sinusoidal (on a smaller scale)
        """
        pass

    async def on_orderbook_update(self) -> None:
        # print("Orderbook update", datetime.now())
        self.pricing_engine_.on_tick()
        asyncio.create_task(self.enter_positions())
        asyncio.create_task(self.try_exit_positions())
        asyncio.create_task(self.buy_or_sell_d())

        self.recent_ticks_.append(pd.Series({
            ticker: self._shared_state.orderbook.wmid(ticker) for ticker in self.config_.tickers
        }))

    async def on_portfolio_update(self) -> None:
        print(f'Portfolio update. New PNL: {self.get_pnl()}')
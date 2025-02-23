from __future__ import annotations

import pandas as pd
import numpy as np

from gt_trading_client import SharedState

from config import Config
from dataclasses import dataclass

@dataclass
class FairValue:
    price: float
    variance: float

    @property
    def sdev(self) -> float:
        return np.sqrt(self.variance)

    def distance_outside_sdevs(self, target_price: float, sdevs: float):
        """
        Return the amount that target_price is outside the target range by.

        e.x. if the fair value is 0 and 1 sdev is $3, this would give the distance
        outside of the interval (-3, 3) that we are in
        """
        sdev = np.sqrt(self.variance)
        lo = self.price - (sdev * sdevs)
        hi = self.price - (sdev + sdevs)

        if target_price < lo:
            return lo - target_price
        elif target_price >= lo and target_price <= hi:
            return 0
        else:
            return target_price - hi


class PricingEngine:
    config_: Config
    historical_data_: pd.DataFrame
    shared_state_: SharedState

    ########################################################################
    # Exponentially weighted moving average related state and computations #
    ########################################################################

    symbol_estimates_: pd.Series = pd.Series([])
    symbol_variances_: pd.Series = pd.Series([])

    def compute_next_exponential_avg(self, new_prices: pd.Series):
        """
        Update new_symbol_estimates_, new_symbol_variants_, prior_prices
        """
        # uninitialized
        if self.symbol_estimates_.empty:
            self.symbol_estimates_ = new_prices
            self.symbol_variances_ = pd.Series({ticker: 0 for ticker in self.config_.tickers})
            return

        smoothing = self.config_.smoothing_factor

        self.symbol_variances_ = (smoothing * abs(new_prices - self.symbol_estimates_)) + (1 - smoothing) * self.symbol_variances_
        self.symbol_estimates_ = (smoothing * new_prices) + (1 - smoothing) * self.symbol_estimates_


    def __init__(self, shared_state: SharedState, historical_data: pd.DataFrame, config: Config):
        """
        @historical_data:
            a time series dataframe (indexed by tick) with columns for
            each symbol.

            historical_data.iloc[0]["AAPL"] will give the price of 
            "AAPL" at tick 0
        """
        self.config_ = config
        self.historical_data_ = historical_data
        self.shared_state_ = shared_state

        for i, row in self.historical_data_.iterrows():
            self.on_new_prices(row.loc[self.config_.tickers])

    def on_new_prices(self, prices: pd.Series):
        """
        prices is a series indexed by ticker name
        """
        self.compute_next_exponential_avg(prices)

    def on_tick(self):
        new_prices = pd.Series({
            ticker: self.shared_state_.orderbook.wmid(ticker) for ticker in self.config_.tickers
        })
        self.on_new_prices(new_prices)

    def fair_values(self) -> pd.Series:
        """
        returns a series of FairValue objects
        """
        return pd.Series({ticker: FairValue(self.symbol_estimates_[ticker], self.symbol_variances_[ticker]) 
                          for ticker in self.config_.tickers})

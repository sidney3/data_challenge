from __future__ import annotations

import pandas as pd
from gt_trading_client import SharedState
from dataclasses import dataclass
from config import Config

@dataclass
class PredictedPrice:
    price: float
    variance: float

class PricingEngine:
    config_: Config
    historical_data_: pd.DataFrame
    shared_state_: SharedState

    ########################################################################
    # Exponentially weighted moving average related state and computations #
    ########################################################################

    symbol_estimates_: pd.Series
    symbol_variants_: pd.Series

    def compute_next_exponential_avg(self, new_prices: pd.Series) -> tuple[pd.Series, pd.Series]:
        """
        Spits out new_symbol_estimates_, new_symbol_variants_
        """
        new_estimates = (self.config_.smoothing_factor * new_prices) + (1 - self.config_.smoothing_factor) * self.symbol_estimates_
        new_variances = (self.config_.smoothing_factor * new_prices) + (1 - self.config_.smoothing_factor) * self.symbol_estimates_

        return new_estimates, new_variances

    def __init__(self, shared_state: SharedState, historical_data: pd.DataFrame, config: Config):
        """
        @historical_data:
            a time series dataframe (indexed by tick) with columns for
            each symbol.

            historical_data.iloc[0]["AAPL"] will give the price of 
            "AAPL" at tick 0
        @config
            a str -> float dict describing the configuration of our
            pricing. Example:

            "smoothing_factor" -> 0.5
        """
        self.config_ = config
        self.historical_data_ = historical_data
        self.shared_state_ = shared_state

    def on_new_prices(self, prices: pd.Series):
        """
        prices is a series indexed by ticker name
        """
        self.symbol_estimates, self.symbol_variances_ = self.compute_next_exponential_avg(prices)

    def fair_values(self) -> tuple[pd.Series, pd.Series]:
        """
        returns a tuple of [EstimatedPrices, Variance]
        """
        return self.symbol_estimates_, self.symbol_variances_

from __future__ import annotations

import pandas as pd

from gt_trading_client import SharedState

from config import Config

class PricingEngine:
    config_: Config
    historical_data_: pd.DataFrame
    shared_state_: SharedState

    ########################################################################
    # Exponentially weighted moving average related state and computations #
    ########################################################################

    symbol_estimates_: pd.Series = None
    symbol_variances_: pd.Series = None
    prior_prices_: pd.Series = None

    def compute_next_exponential_avg(self, new_prices: pd.Series):
        """
        Update new_symbol_estimates_, new_symbol_variants_, prior_prices
        """
        if not self.prior_prices_:
            self.prior_prices_ = new_prices
            self.symbol_estimates_ = new_prices
            self.symbol_variances_ = pd.Series({ticker: 0 for ticker in self.config_.tickers})
            return

        smoothing = self.config_.smoothing_factor

        self.symbol_estimates_ = (smoothing * new_prices) + (1 - smoothing) * self.symbol_estimates_
        self.symbol_variances_ = (smoothing * (new_prices - self.prior_prices_)) + (1 - smoothing) * self.symbol_variances_
        self.prior_prices_ = new_prices

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

        for row in self.historical_data_:
            self.on_new_prices(row)
            print(f'fair values after latest data sample: {self.fair_values()}')

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

    def fair_values(self) -> tuple[pd.Series, pd.Series]:
        """
        returns a tuple of [EstimatedPrices, Variance]
        """
        return self.symbol_estimates_, self.symbol_variances_

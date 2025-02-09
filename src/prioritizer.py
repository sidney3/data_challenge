from src.trading_client import TradingClient
from collections import deque

import time

class Prioritizer:
    def __init__(self, rate_limit: int, trading_client: TradingClient) -> None:
        self._rate_limit = rate_limit
        self._trading_client = trading_client
        self._rate_limit_window = deque()

    def _update_rate_limit_window(self) -> None:
        current_time = time.time()
        while self._rate_limit_window and self._rate_limit_window[0] < current_time - 1:
            self._rate_limit_window.popleft()

    def place_limit(self, ticker: str, volume: float, price: float, is_bid: bool) -> None:
        self._update_rate_limit_window()
        if len(self._rate_limit_window) >= self._rate_limit:
            print(f"Limit order with params {ticker}, {volume}, {price} rejected due to rate limit") 
            return
        self._rate_limit_window.append(time.time())
        self._trading_client.place_limit(ticker, volume, price, is_bid)

    def place_market(self, ticker: str, volume: float, is_bid: bool) -> None:
        self._update_rate_limit_window()
        if len(self._rate_limit_window) >= self._rate_limit:
            print(f"Market order with params {ticker}, {volume} rejected due to rate limit") 
            return
        self._rate_limit_window.append(time.time())
        self._trading_client.place_market(ticker, volume, is_bid)
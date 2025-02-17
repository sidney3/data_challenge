from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class OrderSide(str, Enum):
    BID = "BID"
    ASK = "ASK"


# Used to represent orders returned from portfolio
@dataclass
class Order:
    ticker: str
    price: float
    volume: float
    side: OrderSide
    id: int


class PlacableOrder(ABC):
    @abstractmethod
    def atomic_params(self) -> dict[str, Any]:
        pass


# Used to represent limit order to be placed
@dataclass
class LimitOrder(PlacableOrder):
    ticker: str
    price: float
    volume: float
    is_bid: bool

    def atomic_params(self) -> dict[str, Any]:
        form_data = {
            "type": "limit_order",
            "ticker": self.ticker,
            "price": self.price,
            "volume": self.volume,
            "bid": self.is_bid,
        }
        return form_data


# Used to represent market order to be placed
@dataclass
class MarketOrder(PlacableOrder):
    ticker: str
    volume: float
    is_bid: bool

    def atomic_params(self) -> dict[str, Any]:
        form_data = {
            "type": "market_order",
            "ticker": self.ticker,
            "volume": self.volume,
            "bid": self.is_bid,
        }
        return form_data


# Used to represent single order removal
@dataclass
class RemoveOrder(PlacableOrder):
    id: int

    def atomic_params(self) -> dict[str, Any]:
        form_data = {
            "type": "remove",
            "orderID": self.id,
        }
        return form_data


# Used to represent remove all
@dataclass
class RemoveAll(PlacableOrder):

    def atomic_params(self) -> dict[str, Any]:
        form_data = {
            "type": "remove_all",
        }
        return form_data

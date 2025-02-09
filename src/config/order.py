from dataclasses import dataclass
from enum import Enum

class OrderSide(str, Enum):
    BID = "BID"
    ASK = "ASK"

@dataclass
class Order:
    ticker: str
    price: float
    volume: float
    side: OrderSide
    id: int
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .shared_state import SharedState
    from .prioritizer import Prioritizer

from abc import ABC
from abc import abstractmethod


class Strategy(ABC):
    def __init__(self, quoter: Prioritizer, shared_state: SharedState):
        self._quoter = quoter
        self._shared_state = shared_state

    async def start(self) -> None:
        await self._quoter.subscribe()

    @abstractmethod
    def on_orderbook_update(self) -> None:
        pass

    @abstractmethod
    def on_portfolio_update(self) -> None:
        pass

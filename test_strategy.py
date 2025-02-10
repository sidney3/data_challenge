from strategy import Strategy
from src.shared_state import SharedState
from src.prioritizer import Prioritizer

class TestStrategy(Strategy):
    def __init__(self, quoter: Prioritizer, shared_state: SharedState):
        super().__init__(quoter, shared_state)

    def on_orderbook_update(self):
        print("Orderbook update")
        self._quoter.place_limit("A", 1, 1, True)

    def on_portfolio_update(self):
        print("Portfolio update")
        pass

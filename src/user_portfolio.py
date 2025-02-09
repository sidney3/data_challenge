from src.config.order import Order

class UserPortfolio:
    def __init__(self):
        self.data = {
            "balance": 0,
            "pnl": 0,
            "positions": {},
            "username": None,
            "Orders": {}
        }

    # Replace the entire portfolio data with a new message
    def update_portfolio(self, message):
        if not isinstance(message, dict):
            print("Invalid message format:", message)
            return

        print(message)

        # Reset the portfolio and set it to the new message
        self.data = {
            "balance": message.get("balance", 0),
            "pnl": message.get("pnl", 0),
            "positions": message.get("positions", {}),  # Replaces completely
            "username": message.get("username"),
            "Orders": {}
        }

        # Process orders if provided
        orders = message.get("Orders")
        if isinstance(orders, dict):
            for ticker, order_list_per_ticker in orders.items():
                self.data["Orders"][ticker] = []
                for order in order_list_per_ticker:
                    order_with_ticker = Order(
                        ticker=ticker,
                        volume=order["volume"],
                        price=order["price"],
                        side=order["side"],
                        id=order["orderId"],
                    )
                    self.data["Orders"][ticker].append(order_with_ticker)

    # Get portfolio snapshot
    def get_portfolio(self):
        return self.data.copy()


# Example
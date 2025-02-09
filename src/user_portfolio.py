class UserPortfolio:
    def __init__(self):
        self.data = {
            "balance": 0,
            "pnl": 0,
            "positions": {},
            "username": None,
            "Orders": []
        }

    # Replace the entire portfolio data with a new message
    def update_portfolio(self, message):
        if not isinstance(message, dict):
            print("Invalid message format:", message)
            return

        print(message)  # Logging the received message

        # Reset the portfolio and set it to the new message
        self.data = {
            "balance": message.get("balance", 0),
            "pnl": message.get("pnl", 0),
            "positions": message.get("positions", {}),  # Replaces completely
            "username": message.get("username"),
            "Orders": []
        }

        # Process orders if provided
        orders = message.get("Orders")
        if isinstance(orders, dict):
            order_list = []
            for ticker, order_list_per_ticker in orders.items():
                for order in order_list_per_ticker:
                    order_with_ticker = dict(order, ticker=ticker)
                    order_list.append(order_with_ticker)
            self.data["Orders"] = order_list

    # Get portfolio snapshot
    def get_portfolio(self):
        return self.data.copy()


# Example
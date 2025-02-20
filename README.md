# Setting Up Environment

## Running Locally
We've provided support for 2 environment tools: venv and pyenv-virtualenv.
### Linux/MacOS
#### venv
If you use `python` alias, run:
`source scripts/env.sh venv`

If you use `python3` alias, run:
`source scripts/env.sh venv --python3`
#### pyenv
If you use `python` alias, run:
`source scripts/env.sh pyenv`

If you use `python3` alias, run:
`source scripts/env.sh pyenv --python3`
### Windows
#### venv
Run the following commands inside an admin powershell.

If you use `python` alias, run:
`. scripts/env.sh venv`

If you use `python3` alias, run:
`. scripts/env.sh venv --python3`
### Without Script
If for whatever reason the script doesn't work, you can manually set up the environment by creating a virtual environment and installing the dependencies inside `scripts/requirements.in`.

## Running in Docker
To start the docker container:
`docker-compose up --build`
Once inside `/app` in the container:
`source scripts/env.sh venv`
Note the container mounts your local file system of the repo to `/app` in the container.

## Adding Dependencies
If you need to add dependencies, add them to `scripts/requirements.in` and run the same commmand you used to setup the environment.

# Exchange Client Program
## Overview
`main.py` is the entry point for the strategy. It is responsible for:
1. Initializing the TradingClient
2. Initializing the SharedState and Prioritizer using the exchange client
3. Initializing the Strategy
4. Passing the Strategy to the TradingClient (will run trigger based strategy)
5. Starting the Strategy (subscribe to exchange websocket streams and run strategy)

## Strategy
There are 2 triggers:
1. Orderbook Update: This trigger is called when the orderbook is updated. The SharedState will contain all updated info. Call the quoter to place trades.
2. Portfolio Update: This trigger is called when a portfolio snapshot (positions, balance, open orders, etc.) is sent. The SharedState will contain all updated info. Call the quoter to place trades.

## Quoter
We have provided a simple quoter that performs client-side rate limiting in `Prioritizer`. You can modify the place order function to implement prioritization logic and decide whether or not to submit trades.

## Filtered Orderbook
The orderbook is stored in the SharedState. The orderbook is, by default, filtered to exclude your own orders. You can access both the raw orderbook if needed, though.

To access the depth of a bid for a particular ticker and price level:
`depth = shared_state.orderbooks[ticker]["bids"][price_level]`

Likewise, to access the depth of an ask:
`depth = shared_state.orderbooks[ticker]["asks"][price_level]`

## User Portfolio
The user portfolio is stored in the SharedState. You can access the your positions, balance, open orders, etc.
The portfolio is stored as a dictionary.

To access the balance of a particular ticker:
`balance = shared_state.portfolio.positions[ticker]`

To access the open orders of a particular ticker:
`open_orders = shared_state.portfolio.orders[ticker]`

To access the balance:
`balance = shared_state.portfolio.balance`

To access the PnL:
`pnl = shared_state.portfolio.pnl`

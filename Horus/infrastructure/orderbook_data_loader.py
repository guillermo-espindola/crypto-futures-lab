import requests
from typing import Optional
from infrastructure.loader_interface import ILoader
from models.orderbook_snapshot import OrderBookSnapshot
from state.orderbook_state import OrderBookState
from utils.logger import Logger

class OrderBookDataLoader(ILoader):
    """
    OrderBook DataLoader
    ------------------
    Fetches the initial local order book snapshot from Binance REST API.
    """

    def __init__(self, symbol: str, limit: int, orderbook_state: OrderBookState, logger: Logger):
        self._symbol = symbol
        self._limit = limit
        self._orderbook_state = orderbook_state
        self._logger = logger
        self._url = "https://fapi.binance.com/fapi/v1/depth"

    def load(self):
        """
        Fetches the snapshot and applies it to the state.
        """
        params = {
            "symbol": self._symbol,
            "limit": self._limit
        }

        try:
            self._logger.info(f"Fetching OrderBook snapshot for {self._symbol} (limit={self._limit})")
            response = requests.get(self._url, params=params)
            response.raise_for_status()
            data = response.json()

            # Correctly use OrderBookSnapshot for the REST API response
            snapshot = OrderBookSnapshot.from_json(data)
            self._orderbook_state.apply_snapshot(self._symbol, snapshot)

            self._logger.info(f"OrderBook snapshot successfully loaded for {self._symbol}")
        except Exception as e:
            self._logger.error(f"Error loading OrderBook snapshot: {e}")
            raise e

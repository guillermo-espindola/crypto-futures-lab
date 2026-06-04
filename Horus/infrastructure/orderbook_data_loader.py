import requests

from infrastructure.loader_interface import ILoader
from models.orderbook_snapshot import OrderBookSnapshot
from state.orderbook_state import OrderBookState
from utils.logger_interface import ILogger

class OrderBookDataLoader(ILoader):

    def __init__(self, symbol: str, limit: int, orderbook_state: OrderBookState, logger: ILogger):
        self._symbol = symbol
        self._limit = limit
        self._orderbook_state = orderbook_state
        self._logger = logger
        self._url = "https://fapi.binance.com/fapi/v1/depth"

    def load(self):

        params = { "symbol": self._symbol,
                    "limit": self._limit }

        try:
            self._logger.info(f"[FETCHING ORDERBOOK] url={self._url} params={params}")
            response = requests.get(self._url, params=params)
            response.raise_for_status()
            data = response.json()

            order_book_snapshot = OrderBookSnapshot.from_json(data)
            self._orderbook_state.apply_snapshot(self._symbol, order_book_snapshot)

        except Exception as e:
            self._logger.error(f"[FETCHING ORDERBOOK] {e}")
            raise e

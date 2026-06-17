import requests

from infrastructure.loader_interface import ILoader
from models.orderbook import OrderBook
from state.orderbook_state import OrderBookState
from utils.logger_interface import ILogger

class OrderBookDataLoader(ILoader):

    def __init__(self, url: str, symbol: str, limit: int, orderbook_state: OrderBookState, logger: ILogger):
        self._symbol = symbol
        self._limit = limit
        self._orderbook_state = orderbook_state
        self._logger = logger
        self._url = url

    def load(self):

        params = { "symbol": self._symbol,
                    "limit": self._limit }

        try:
            self._logger.info(f"[FETCHING ORDERBOOK] url={self._url} params={params}")
            response = requests.get(self._url, params=params)
            response.raise_for_status()
            data = response.json()

            order_book = OrderBook.from_json(data)
            self._logger.info(f"[LOAD ORDERBOOK]{order_book}")
            self._orderbook_state.set_orderbook(order_book)

        except Exception as e:
            self._logger.error(f"[FETCHING ORDERBOOK] {e}")
            raise e

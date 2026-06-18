
import requests

from infrastructure.loader_interface import ILoader
from models.aggregate_trade_snapshot import AggregateTradeSnapshot
from models.aggregate_trade import AggregateTrade
from state.market_state import MarketState
from utils.logger_interface import ILogger

class AggregateTradesDataLoader(ILoader):
    def __init__(self, url: str, symbol: str, limit: int, market_state: MarketState, logger: ILogger):
        self._symbol = symbol
        self._limit = limit
        self._market_state = market_state
        self._logger = logger
        self._url = url

    def load(self):

        params = { "symbol": self._symbol,
                    "limit": self._limit }

        try:
            self._logger.info(f"[FETCHING AGGREGATE TRADES] url={self._url} params={params}")
            response = requests.get(self._url, params=params)
            response.raise_for_status()
            data = response.json()
            self._logger.info(f"[DATA] {data}")
            
            for aggTrade in data:
                aggregate_trade_snapshot = AggregateTradeSnapshot.from_json(aggTrade)
                self._logger.info(f"[LOAD DATA]{aggregate_trade_snapshot}")
                self._market_state.add_custom_candle(AggregateTrade(
                    aggregate_trade_id=aggregate_trade_snapshot.aggregate_trade_id,
                    event_time=aggregate_trade_snapshot.timestamp,
                    quantity=aggregate_trade_snapshot.quantity,
                    price=aggregate_trade_snapshot.price,
                    first_trade_id=aggregate_trade_snapshot.first_trade_id,
                    is_buyer_maker=aggregate_trade_snapshot.is_buyer_maker,
                    last_trade_id=aggregate_trade_snapshot.last_trade_id,
                    symbol=self._symbol,
                    trade_time=aggregate_trade_snapshot.timestamp
                ))

        except Exception as e:
            self._logger.error(f"[FETCHING AGGREGATE TRADES] {e}")
            raise e
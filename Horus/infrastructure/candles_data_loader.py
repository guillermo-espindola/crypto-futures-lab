
import requests

from datetime import datetime, timezone

from infrastructure.loader_interface import ILoader
from models.candle import Candle
from state.candles_state import CandlesState
from utils.logger_interface import ILogger

class CandlesDataLoader(ILoader):
    def __init__(self, symbol: str,
                 time_frames: list[str],
                 max_candles: int,
                 candles_state: CandlesState,
                 logger: ILogger):
        self._symbol = symbol
        self._time_frames = time_frames
        self._max_candles = max_candles,
        self._candles_state = candles_state
        self._url = 'https://www.binance.com/fapi/v1/klines'
        self._logger = logger

    def _fetch_candles(self, symbol : str,
            timeframe : str,
            quantity : int,
            last_timestamp : int):

        params = {
            'symbol': symbol,
            'interval': timeframe,
            'limit': quantity,
            'endTime': last_timestamp
        }

        try:
            self._logger.info(f"[FETCHING CANDLES] url={self._url} params={params}")
            response = requests.get(self._url, params=params)
            response.raise_for_status()
            raw_data = response.json()

            keys = [
                "openTime",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "closeTime",
                "quoteAssetVolume",
                "numberOfTrades",
                "takerBuyBaseAssetVolume",
                "takerBuyQuoteAssetVolume"
            ]

            float_fields = {
                "open", "high", "low", "close", "volume",
                "quoteAssetVolume",
                "takerBuyBaseAssetVolume",
                "takerBuyQuoteAssetVolume"
            }

            int_fields = {
                "openTime", "closeTime", "numberOfTrades"
            }

            result = []

            for row in raw_data:
                item = {}
                for key, value in zip(keys, row):
                    if key in float_fields:
                        item[key] = float(value)
                    elif key in int_fields:
                        item[key] = int(value)
                    else:
                        item[key] = value
                result.append(item)

            return result

        except Exception as exception:
            self._logger.error(f"[FETCHING CANDLES] {exception}")

    def load(self):
        current_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        for time_frame in self._time_frames:

            candlesResult = self._fetch_candles(self._symbol,
                                                time_frame, 
                                                self._max_candles, 
                                                current_timestamp)
            for candleResult in candlesResult:

                candle = Candle(
                    symbol=self._symbol,
                    timeframe=time_frame,

                    open_time=candleResult["openTime"],
                    close_time=candleResult["closeTime"],

                    open=candleResult["open"],
                    high=candleResult["high"],
                    low=candleResult["low"],
                    close=candleResult["close"],

                    volume=candleResult["volume"],

                    quote_asset_volume=candleResult["quoteAssetVolume"],

                    trades=candleResult["numberOfTrades"],

                    taker_buy_base_volume=candleResult["takerBuyBaseAssetVolume"],
                    taker_buy_quote_volume=candleResult["takerBuyQuoteAssetVolume"],

                    is_closed=True
                )

                self._candles_state.add(candle)

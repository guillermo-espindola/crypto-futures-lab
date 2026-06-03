import requests

from state.market_state import MarketState
from models.candle import Candle
from datetime import datetime, timezone

from utils.logger_interface import ILogger

class MarketDataLoader:
    def __init__(self, max_length: int,
                 market_state: MarketState,
                 logger: ILogger):
        self._max_length = max_length
        self._market_state = market_state
        self._logger = logger
        self.url : str = 'https://www.binance.com/fapi/v1/klines'
        self.symbol : str = 'UBUSDT'
        self.timeframe : str = '1m'
        self.quantity : int = 720 #720
        self.current_timestamp : int = int(datetime.now(timezone.utc).timestamp() * 1000)

    def load_candle_chart(self):
        self._logger.info(f"Loading initial data for {self.symbol}...")
        candlesResult = self._fetch_historical_candles(self.symbol, self.timeframe, self.quantity, self.current_timestamp)
        for candleResult in candlesResult:

            candle = Candle(
                symbol=self.symbol,
                timeframe=self.timeframe,

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

            self._market_state.add_candle(candle)
    
    def _fetch_historical_candles(self, symbol : str,
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
            response = requests.get(self.url, params=params)
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
            print('Error getting candlestick data:', exception)
            return None
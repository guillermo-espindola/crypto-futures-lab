from models.candle import Candle
from models.aggregate_trade import AggregateTrade
from models.orderbook_depth_update import OrderBookDepthUpdate
from models.liquidation import Liquidation
from models.trade import Trade
from state.market_state import MarketState
from utils.logger_interface import ILogger

class EventDispatcher:
    def __init__(self, market_state: MarketState, logger: ILogger):
        self._market_state = market_state
        self._logger = logger

    def dispatch(self, event: dict):
        try:
            event_type = event.get("e")

            if event_type == "kline":
                candle = Candle.from_json(event)
                self._market_state.add_candle(candle)

            elif event_type == "aggTrade":
                aggregate_trade = AggregateTrade.from_json(event)
                self._market_state.set_current_price(aggregate_trade.price)
                self._market_state.add_aggregate_trade(aggregate_trade)
            
            elif event_type == "trade":
                self._market_state.add_trade(Trade.from_json(event))

            elif event_type == "depthUpdate":
                self._market_state.update_orderbook(OrderBookDepthUpdate.from_json(event))

            elif event_type == "forceOrder":
                self._market_state.add_liquidation(Liquidation.from_json(event))

            else:
                self._logger.error(f"[dispatch] Unknown event type: {event_type}")

        except Exception as e:
            self._logger.error(f"[dispatch] {e}")

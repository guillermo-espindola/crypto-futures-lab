from models.candle import Candle
from models.aggregate_trade import AggregateTrade
from models.orderbook import OrderBook
from models.liquidation import Liquidation
from models.trade import Trade
from state.market_state import MarketState
from utils.logger_interface import ILogger

class EventDispatcher:
    def __init__(self, market_state: MarketState, logger: ILogger):
        self.market_state = market_state
        self.logger = logger

    def dispatch(self, event: dict):
        try:
            event_type = event.get("e")

            if event_type == "kline":
                self.market_state.add_candle(Candle.from_json(event))

            elif event_type == "aggTrade":
                self.market_state.add_aggregate_trade(AggregateTrade.from_json(event))
            
            elif event_type == "trade":
                self.market_state.add_trade(Trade.from_json(event))

            elif event_type == "depthUpdate":
                self.market_state.add_orderbook(OrderBook.from_json(event))

            elif event_type == "forceOrder":
                self.market_state.add_liquidation(Liquidation.from_json(event))

            else:
                self.logger.error(f"[DISPATCH] Unknown event type: {event_type}")

        except Exception as e:
            self.logger.error(f"[DISPATCH] {e}")

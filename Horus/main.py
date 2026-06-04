import asyncio
from app.trading_loop import TradingLoop

from notification.toast_notifier import ToastNotifier
from utils.config_manager import ConfigManager
from utils.logger import Logger

from engines.execution_engine import ExecutionEngine
from engines.liquidity_engine import LiquidityEngine
from engines.order_flow_engine import OrderFlowEngine
from engines.order_book_engine import OrderBookEngine
from engines.portfolio_engine import PortfolioEngine
from engines.regime_engine import RegimeEngine
from engines.risk_engine import RiskEngine
from engines.scoring_engine import ScoringEngine
from engines.structure_engine import StructureEngine

from infrastructure.candles_data_loader import CandlesDataLoader
from infrastructure.orderbook_data_loader import OrderBookDataLoader
from infrastructure.event_dispatcher import EventDispatcher
from infrastructure.kafka_consumer import KafkaConsumer

from state.candles_state import CandlesState
from state.orderbook_state import OrderBookState
from state.market_state import MarketState
from utils.logger_file import LoggerFile

async def main():
    # 1. CONFIGURATION
    config_manager = ConfigManager()
    general_settings = config_manager.settings.general

    symbol = general_settings["symbol"]
    time_frame = general_settings["time_frame"]
    time_frames = general_settings["time_frames"]
    max_candles = general_settings["max_candles"]
    initial_balance = general_settings["initial_balance"]

    # 2. STATE
    candles_state = CandlesState(max_candles, Logger(CandlesState))
    order_book_state = OrderBookState()
    market_state = MarketState(symbol, candles_state, order_book_state)

    # 3. LOADER & CONSUMER
    candles_data_loader = CandlesDataLoader(symbol, time_frames, max_candles, candles_state, Logger(CandlesDataLoader))
    orderbook_data_loader = OrderBookDataLoader(symbol, 100, order_book_state, Logger(OrderBookDataLoader))
    event_dispatcher = EventDispatcher(market_state, Logger(EventDispatcher))
    kafka_consumer = KafkaConsumer(
        [
        "Candles",
        "Trades",
        "Orderbook",
        "Liquidations",
        "AggregateTrades"
    ], # Topics list usually handled inside or in config.json
        "localhost:29092",
        "hft-trading-loop",
        event_dispatcher,
        Logger(KafkaConsumer)
    )
    # Note: In a real scenario, we'd use the exact values from config.json general/kafka section
    # For now, we use defaults or the JSON config mapping.

    # 4. ENGINES (Hierarchical dependency)
    regime_engine = RegimeEngine(market_state, symbol, time_frame)
    structure_engine = StructureEngine(market_state, symbol, time_frame)
    liquidity_engine = LiquidityEngine(market_state, symbol, time_frame)
    order_flow_engine = OrderFlowEngine(market_state, symbol, Logger(OrderFlowEngine))
    order_book_engine = OrderBookEngine(market_state, symbol)

    scoring_engine = ScoringEngine(
        structure_engine,
        liquidity_engine,
        order_flow_engine,
        regime_engine,
        order_book_engine,
        Logger(ScoringEngine)
    )

    portfolio_engine = PortfolioEngine(initial_balance, Logger(PortfolioEngine))
    risk_engine = RiskEngine()

    execution_engine = ExecutionEngine(
        market_state,
        portfolio_engine,
        risk_engine
    )

    # 5. NOTIFIER
    notifier = ToastNotifier(LoggerFile(ToastNotifier))

    # 6. TRADING LOOP
    trading_loop = TradingLoop(
        symbol,
        market_state,
        kafka_consumer,
        structure_engine,
        liquidity_engine,
        order_flow_engine,
        regime_engine,
        order_book_engine,
        scoring_engine,
        portfolio_engine,
        risk_engine,
        execution_engine,
        notifier,
        Logger(TradingLoop)
    )

    try:
        notifier.notify("*** HORUS ***")
        candles_data_loader.load()
        orderbook_data_loader.load()
        candles_state.new_candle_event.subscribe(trading_loop.on_new_candle)
        portfolio_engine.open_position_event.subscribe(trading_loop.on_open_position)

        await kafka_consumer.start()
        await trading_loop.run(sleep_time=0.5)
    except KeyboardInterrupt:
        print("\nStopping trading loop...")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"ERROR: {e}")

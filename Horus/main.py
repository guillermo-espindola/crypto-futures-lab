import asyncio

from app.trading_loop import TradingLoop

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
from infrastructure.event_dispatcher import EventDispatcher
from infrastructure.kafka_consumer import KafkaConsumer
from infrastructure.orderbook_data_loader import OrderBookDataLoader

from notification.toast_notifier import ToastNotifier

from state.candles_state import CandlesState
from state.market_state import MarketState
from state.orderbook_state import OrderBookState

from utils.config_manager import ConfigManager
from utils.logger import Logger
from utils.logger_settings import LoggerSettings

async def main():
    # 1. CONFIGURATION
    path_config_file = "config.json"
    logger_settings = LoggerSettings(enable_file_logging=True, enable_console_logging=True)
    config_manager = ConfigManager(path_config_file, Logger(ConfigManager, logger_settings))
    general_settings = config_manager.settings.general


    symbol = general_settings["symbol"]
    time_frame = general_settings["time_frame"]
    time_frames = general_settings["time_frames"]
    max_candles = general_settings["max_candles"]
    initial_balance = general_settings["initial_balance"]

    # 2. STATE
    candles_state = CandlesState(max_candles, Logger(CandlesState, logger_settings))
    order_book_state = OrderBookState(Logger(OrderBookState, logger_settings))
    market_state = MarketState(symbol, candles_state, order_book_state)

    # 3. LOADER & CONSUMER
    candles_data_loader = CandlesDataLoader(symbol, time_frames, max_candles, candles_state, Logger(CandlesDataLoader, logger_settings))
    orderbook_data_loader = OrderBookDataLoader(symbol, 100, order_book_state, Logger(OrderBookDataLoader, logger_settings))
    event_dispatcher = EventDispatcher(market_state, Logger(EventDispatcher, logger_settings))
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
        Logger(KafkaConsumer, logger_settings)
    )
    # Note: In a real scenario, we'd use the exact values from config.json general/kafka section
    # For now, we use defaults or the JSON config mapping.

    # 4. ENGINES (Hierarchical dependency)
    regime_engine = RegimeEngine(market_state, symbol, time_frame, config_manager, Logger(RegimeEngine, logger_settings))
    structure_engine = StructureEngine(market_state, symbol, time_frame, config_manager, Logger(StructureEngine, logger_settings))
    liquidity_engine = LiquidityEngine(market_state, symbol, time_frame, config_manager)
    order_flow_engine = OrderFlowEngine(market_state, symbol, config_manager, Logger(OrderFlowEngine, logger_settings))
    order_book_engine = OrderBookEngine(market_state, symbol, config_manager)

    scoring_engine = ScoringEngine(
        structure_engine,
        liquidity_engine,
        order_flow_engine,
        regime_engine,
        order_book_engine,
        config_manager,
        Logger(ScoringEngine, logger_settings)
    )

    portfolio_engine = PortfolioEngine(initial_balance, Logger(PortfolioEngine, logger_settings))
    risk_engine = RiskEngine(config_manager, Logger(RiskEngine, logger_settings))

    execution_engine = ExecutionEngine(
        market_state,
        portfolio_engine,
        risk_engine,
        config_manager
    )

    # 5. NOTIFIER
    notifier = ToastNotifier(Logger(ToastNotifier, logger_settings))

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
        config_manager,
        Logger(TradingLoop, logger_settings)
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

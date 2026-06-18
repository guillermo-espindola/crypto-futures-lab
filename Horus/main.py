import asyncio

from app.trading_loop import TradingLoop

from config.config_manager import ConfigManager

from engines.execution_engine import ExecutionEngine
from engines.liquidity_engine import LiquidityEngine
from engines.order_flow_engine import OrderFlowEngine
from engines.order_book_engine import OrderBookEngine
from engines.portfolio_engine import PortfolioEngine
from engines.regime_engine import RegimeEngine
from engines.risk_engine import RiskEngine
from engines.scoring_engine import ScoringEngine
from engines.structure_engine import StructureEngine

from infrastructure.aggregate_trades_data_loader import AggregateTradesDataLoader
from infrastructure.candles_data_loader import CandlesDataLoader
from infrastructure.event_dispatcher import EventDispatcher
from infrastructure.kafka_consumer import KafkaConsumer
from infrastructure.orderbook_data_loader import OrderBookDataLoader

from notification.toast_notifier import ToastNotifier

from state.candles_state import CandlesState
from state.market_state import MarketState
from state.orderbook_state import OrderBookState
from state.aggregate_trade_state import AggregateTradeState
from state.liquidation_state import LiquidationState
from state.trade_state import TradeState

from utils.aggregate_trade_candle_builder import AggregateTradeCandleBuilder
from utils.logger import Logger
from utils.logger_settings import LoggerSettings

async def main():
    logger_settings_console = LoggerSettings(enable_file_logging=False, enable_console_logging=True)
    logger_settings_file = LoggerSettings(enable_file_logging=True, enable_console_logging=False)

    config_manager = ConfigManager("config.json", Logger(ConfigManager, logger_settings_console))
    app_config = config_manager.get_config()

    symbol = app_config.market.symbol
    time_frame = app_config.market.timeframe
    time_frames = app_config.market.timeframes
    max_candles = app_config.market.max_candles
    max_orderbook_depth = app_config.market.max_orderbook_depth
    max_agg_trades = app_config.market.max_agg_trades
    max_liquidations = app_config.market.max_liquidations
    max_trades = app_config.market.max_trades
    initial_balance = app_config.portfolio.initial_balance
    window_size = app_config.order_flow.window_size

    history_candles_endpoint = app_config.history.candles_endpoint
    history_orderbook_endpoint = app_config.history.orderbook_depth_endpoint
    history_aggregate_trades_endpoint = app_config.history.aggregate_trades_endpoint

    kafka_topics = app_config.kafka.topics
    kafka_bootstrap_server = app_config.kafka.bootstrap_server
    kafka_group_id = app_config.kafka.group_id

    candles_state = CandlesState(max_candles,
                                 Logger(CandlesState, logger_settings_file))
    order_book_state = OrderBookState(Logger(OrderBookState, logger_settings_console))
    aggregate_trade_state = AggregateTradeState(max_agg_trades)
    liquidation_state = LiquidationState(max_liquidations)
    trades_state = TradeState(max_trades)

    aggregate_trade_candle_builder = AggregateTradeCandleBuilder(10, candles_state, Logger(AggregateTradeCandleBuilder, logger_settings_console))

    market_state = MarketState(candles_state,
                               order_book_state,
                               aggregate_trade_state,
                               liquidation_state,
                               trades_state,
                               aggregate_trade_candle_builder)

    # 3. LOADER & CONSUMER

    aggregate_trades_data_loader = AggregateTradesDataLoader(history_aggregate_trades_endpoint, symbol, max_agg_trades, market_state, Logger(AggregateTradesDataLoader, logger_settings_file))

    candles_data_loader = CandlesDataLoader(history_candles_endpoint,
                                            symbol,
                                            time_frames,
                                            max_candles,
                                            candles_state,
                                            Logger(CandlesDataLoader, logger_settings_console))
    orderbook_data_loader = OrderBookDataLoader(history_orderbook_endpoint, symbol, max_orderbook_depth, order_book_state, Logger(OrderBookDataLoader, logger_settings_console))
    event_dispatcher = EventDispatcher(market_state,
                                       Logger(EventDispatcher, logger_settings_console))
    kafka_consumer = KafkaConsumer( kafka_topics, 
                                   kafka_bootstrap_server,
                                   kafka_group_id,
                                   event_dispatcher,
                                   Logger(KafkaConsumer, logger_settings_console))

    # 4. ENGINES (Hierarchical dependency)
    regime_engine = RegimeEngine(market_state, time_frame, config_manager, Logger(RegimeEngine, logger_settings_console))
    structure_engine = StructureEngine(market_state, time_frame, config_manager, Logger(StructureEngine, logger_settings_console))
    liquidity_engine = LiquidityEngine(market_state, time_frame, config_manager)
    order_flow_engine = OrderFlowEngine(market_state, window_size, Logger(OrderFlowEngine, logger_settings_console))
    order_book_engine = OrderBookEngine(market_state, config_manager)

    scoring_engine = ScoringEngine(
        structure_engine,
        liquidity_engine,
        order_flow_engine,
        regime_engine,
        order_book_engine,
        config_manager,
        Logger(ScoringEngine, logger_settings_console)
    )

    portfolio_engine = PortfolioEngine(initial_balance, Logger(PortfolioEngine, logger_settings_console))
    risk_engine = RiskEngine(config_manager, Logger(RiskEngine, logger_settings_console))

    execution_engine = ExecutionEngine(
        market_state,
        portfolio_engine,
        risk_engine,
        config_manager
    )

    # 5. NOTIFIER
    notifier = ToastNotifier(Logger(ToastNotifier, logger_settings_file))

    # 6. TRADING LOOP
    trading_loop = TradingLoop(
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
        Logger(TradingLoop, logger_settings_console)
    )

    try:
        notifier.notify("[HORUS]")
        aggregate_trades_data_loader.load()
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

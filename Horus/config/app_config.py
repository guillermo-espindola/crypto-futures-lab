from dataclasses import dataclass

from config.behavior_config import BehaviorConfig
from config.execution_config import ExecutionConfig
from config.history_config import HistoryConfig
from config.consumer_config import ConsumerConfig
from config.liquidity_config import LiquidityConfig
from config.logger_config import LoggerConfig
from config.market_config import MarketConfig
from config.order_flow_config import OrderFlowConfig
from config.portfolio_config import PortfolioConfig
from config.regime_config import RegimeConfig
from config.risk_config import RiskConfig
from config.scoring_config import ScoringConfig
from config.structure_config import StructureConfig
from config.telegram_config import TelegramConfig

@dataclass(frozen=True)
class AppConfig:
    market: MarketConfig
    history: HistoryConfig
    portfolio: PortfolioConfig
    risk: RiskConfig
    regime: RegimeConfig
    structure: StructureConfig
    scoring: ScoringConfig
    liquidity: LiquidityConfig
    order_flow: OrderFlowConfig
    execution: ExecutionConfig
    behavior: BehaviorConfig
    consumer: ConsumerConfig
    telegram: TelegramConfig
    logger: LoggerConfig

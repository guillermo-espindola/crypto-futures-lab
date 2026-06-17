import json

from config.behavior_config import BehaviorConfig
from config.execution_config import ExecutionConfig
from config.history_config import HistoryConfig
from config.kafka_config import KafkaConfig
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
from config.app_config import AppConfig

from utils.logger_interface import ILogger

class ConfigManager:
    def __init__(self, config_file: str, logger: ILogger):
        self._config_file = config_file
        self._logger = logger
        self._app_config = self._load_config()
    
    def _load_config(self) -> AppConfig:
        try:
            with open(self._config_file, "r") as file:
                config = json.load(file)

            return AppConfig(
                market=MarketConfig(**config["market"]),
                history=HistoryConfig(**config["history"]),
                portfolio=PortfolioConfig(**config["portfolio"]),
                risk=RiskConfig(**config["risk"]),
                regime=RegimeConfig(**config["regime"]),
                structure=StructureConfig(**config["structure"]),
                scoring=ScoringConfig(**config["scoring"]),
                liquidity=LiquidityConfig(**config["liquidity"]),
                order_flow=OrderFlowConfig(**config["order_flow"]),
                execution=ExecutionConfig(**config["execution"]),
                behavior=BehaviorConfig(**config["behavior"]),
                kafka=KafkaConfig(**config["kafka"]),
                telegram=TelegramConfig(**config["telegram"]),
                logger=LoggerConfig(**config["logger"])
                )
        
        except Exception as e:
            self._logger.error(f"[LOAD CONFIG] file={self._config_file} {e}")

    def get_config(self) -> AppConfig:
        return self._app_config
import json
from dataclasses import dataclass
from typing import Any, Dict
from utils.logger_interface import ILogger

@dataclass
class SystemConfig:
    mode: str
    risk: Dict[str, Any]
    scoring: Dict[str, Any]
    liquidity: Dict[str, Any]
    order_flow: Dict[str, Any]
    execution: Dict[str, Any]
    behavior: Dict[str, Any]
    general: Dict[str, Any]

class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self,config_path: str , logger: ILogger):
        if hasattr(self, "_initialized"):
            return

        self.config_path = config_path
        self._logger = logger
        self.settings: SystemConfig = self._load_config()
        self._initialized = True

    def _load_config(self) -> SystemConfig:
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)

            mode = data.get("current_mode", "MODERATE")
            mode_settings = data["modes"].get(mode, data["modes"]["MODERATE"])
            general = data.get("general", {})

            return SystemConfig(
                mode=mode,
                risk=mode_settings["risk"],
                scoring=mode_settings["scoring"],
                liquidity=mode_settings["liquidity"],
                order_flow=mode_settings["order_flow"],
                execution=mode_settings["execution"],
                behavior=mode_settings["behavior"],
                general=general
            )
        except Exception as e:
            self._logger.error(f"Failed to load config from {self.config_path}: {e}. Using defaults.")
            # Fallback to basic defaults if file is missing or corrupt
            return self._get_defaults()

    def _get_defaults(self) -> SystemConfig:
        return SystemConfig(
            mode="MODERATE",
            risk={"max_risk_per_trade": 0.01, "max_leverage": 5, "max_drawdown": 0.15},
            scoring={"ema_alpha": 0.25, "confirmation_threshold": 2, "long_bias_weight": 0.6, "flow_weight": 0.3, "regime_weight": 0.1},
            liquidity={"lookback_period": 30, "sweep_sensitivity": 0.75},
            order_flow={"window_size": 50, "impact_sensitivity": 1.0},
            execution={"slippage_factor": 0.0005, "latency_ms": 50, "taker_fee": 0.0004},
            behavior={"allow_more_trades": "balanced", "cooldown_seconds": 10, "noise_tolerance": "medium"},
            general={"symbol": "UBUSDT", "time_frame": "1m", "time_frames": ["1m", "3m", "5m", "15m", "30m", "1h"], "max_candles": 1000, "initial_balance": 10000.0}
        )

    def get(self, category: str, key: str) -> Any:
        category_map = {
            "risk": self.settings.risk,
            "scoring": self.settings.scoring,
            "liquidity": self.settings.liquidity,
            "order_flow": self.settings.order_flow,
            "execution": self.settings.execution,
            "behavior": self.settings.behavior,
            "general": self.settings.general
        }
        return category_map.get(category, {}).get(key)

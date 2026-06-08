from dataclasses import dataclass

@dataclass(frozen=True)
class RiskConfig:
    max_risk_per_trade: float
    max_leverage: float
    max_drawdown: float
    max_total_exposure: float
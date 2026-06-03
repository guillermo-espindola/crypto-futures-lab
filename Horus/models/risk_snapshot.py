from dataclasses import dataclass


@dataclass(slots=True)
class RiskSnapshot:

    timestamp: int

    max_drawdown: float

    portfolio_heat: float

    leverage: float

    current_risk: float

    exposure: float

    margin_ratio: float

    kill_switch_active: bool
from dataclasses import dataclass

@dataclass(frozen=True)
class OrderFlowConfig:
    window_size: int
    impact_sensitivity: float
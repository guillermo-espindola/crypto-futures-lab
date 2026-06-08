from dataclasses import dataclass

@dataclass(frozen=True)
class BehaviorConfig:
    allow_more_trades: bool
    cooldown_seconds: int
    noise_tolerance: str
from dataclasses import dataclass

@dataclass(frozen=True)
class RegimeConfig:
    default_period: int
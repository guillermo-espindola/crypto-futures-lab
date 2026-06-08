from dataclasses import dataclass

@dataclass(frozen=True)
class PortfolioConfig:
    initial_balance: float
    
from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionConfig:
    slippage_factor: float
    latency_ms: int
    taker_fee: float    
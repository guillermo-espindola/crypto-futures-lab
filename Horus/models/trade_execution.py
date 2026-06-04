from dataclasses import dataclass


@dataclass(slots=True)
class TradeExecution:

    side: str

    execution_price: float

    quantity: float

    slippage: float

    fees: float

    latency_ms: int

    timestamp: int

    success: bool
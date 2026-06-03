from dataclasses import dataclass


@dataclass(slots=True)
class Signal:

    symbol: str

    side: str

    confidence: float

    timestamp: int

    price: float

    timeframe: str

    strategy: str

    def validate(self):

        if self.side not in [
            "LONG",
            "SHORT",
            "NONE"
        ]:
            raise ValueError(
                "Invalid side"
            )

        if (
            self.confidence < 0
            or
            self.confidence > 1
        ):
            raise ValueError(
                "Confidence out of range"
            )
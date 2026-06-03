from dataclasses import dataclass

from models.position_type import PositionType


@dataclass(slots=True)
class Signal:

    symbol: str

    position_type: PositionType

    confidence: float

    timestamp: int

    price: float

    timeframe: str

    strategy: str

    def validate(self):

        if self.position_type not in [
            PositionType.LONG,
            PositionType.SHORT,
            PositionType.NONE
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
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class ConsumerConfig:
    id: str
    type: str
    connection_string: str
    sources: List[str]

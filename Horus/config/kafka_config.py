from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class KafkaConfig:
    bootstrap_server: str
    topics: List[str]
    group_id: str

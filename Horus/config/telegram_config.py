from dataclasses import dataclass

@dataclass(frozen=True)
class TelegramConfig:
    token: str
    chat_id: str
    api_url: str
from dataclasses import dataclass

@dataclass(frozen=True)
class LoggerConfig:
    enable_file_logging: bool
    enable_console_logging: bool
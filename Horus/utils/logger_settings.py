from dataclasses import dataclass

@dataclass(slots=True)
class LoggerSettings:
    enable_file_logging: bool = True
    enable_console_logging: bool = True
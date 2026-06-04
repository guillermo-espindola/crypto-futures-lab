import logging
import os

from logging.handlers import RotatingFileHandler
from typing import Any
from utils.logger_interface import ILogger
from utils.logger_settings import LoggerSettings

class Logger(ILogger):
    def __init__(self, type: Any, logger_settings: LoggerSettings):
        self._name = type.__name__ if hasattr(type, "__name__") else str(type)
        self._logger_settings = logger_settings

        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(logging.INFO)

        if not self._logger.handlers:
            formatter = logging.Formatter(
                "[%(asctime)s]"
                "[%(levelname)s]"
                "[%(name)s] "
                "%(message)s"
            )

            if self._logger_settings.enable_console_logging:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self._logger.addHandler(console_handler)

            if self._logger_settings.enable_file_logging:
                os.makedirs("./logs", exist_ok=True)

                file_handler = RotatingFileHandler(
                    filename=f"./logs/{self._name}.log",
                    maxBytes=1024 * 1024,
                    backupCount=2,
                    encoding="utf-8"
                    )
                file_handler.setFormatter(formatter)
                self._logger.addHandler(file_handler)

            self._logger.info(f"[CREATED LOGGER] {self._name}")

    def info(self, message: str):
        self._logger.info(message)

    def error(self, message: str):
        self._logger.error(message)
import logging
import os

from logging.handlers import RotatingFileHandler
from typing import Any
from utils.logger_interface import ILogger

class Logger(ILogger):
    def __init__(self, type: Any):
        self._name = type.__name__ if hasattr(type, "__name__") else str(type)

        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(logging.INFO)

        if not self._logger.handlers:
            formatter = logging.Formatter(
                "[%(asctime)s]"
                "[%(levelname)s]"
                "[%(name)s] "
                "%(message)s"
            )

            os.makedirs("./logs", exist_ok=True)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            file_handler = RotatingFileHandler(
                filename=f"./logs/{self._name}.log",
                maxBytes=64 * 1024,
                backupCount=2,
                encoding="utf-8"
            )
            file_handler.setFormatter(formatter)

            self._logger.addHandler(console_handler)
            self._logger.addHandler(file_handler)

    def info(self, message: str):
        self._logger.info(message)

    def error(self, message: str):
        self._logger.error(message)
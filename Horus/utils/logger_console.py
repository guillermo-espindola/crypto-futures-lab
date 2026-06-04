import logging

from typing import Any
from utils.logger_interface import ILogger

class LoggerConsole(ILogger):
    def __init__(self, type: Any):
        self._name = type.__name__ if hasattr(type, '__name__') else str(type)
        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(logging.INFO)
        if not self._logger.handlers:

            formatter = logging.Formatter(
                "[%(asctime)s]"
                "[%(levelname)s]"
                "[%(name)s] "
                "%(message)s"
            )

            handler = logging.StreamHandler()

            handler.setFormatter(formatter)

            self._logger.addHandler(handler)

    def info(self, message: str):
        self._logger.info(message)
    
    def error(self, message: str):
        self._logger.error(message)
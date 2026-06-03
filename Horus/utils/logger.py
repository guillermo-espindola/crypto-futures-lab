import logging
from typing import Any
from utils.logger_interface import ILogger

class Logger(ILogger):
    def __init__(self, type: Any):
        self.name = type.__name__ if hasattr(type, '__name__') else str(type)
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:

            formatter = logging.Formatter(
                "[%(asctime)s]"
                "[%(levelname)s]"
                "[%(name)s] "
                "%(message)s"
            )

            handler = logging.StreamHandler()

            handler.setFormatter(formatter)

            self.logger.addHandler(handler)

    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
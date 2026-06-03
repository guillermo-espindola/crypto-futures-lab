import logging
from typing import Any
from utils.logger_interface import ILogger

class LoggerFile(ILogger):
    def __init__(self, type: Any):
        self.name = type.__name__ if hasattr(type, '__name__') else str(type)
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            # 1. Definir el formato del mensaje
            formatter = logging.Formatter(
                "[%(asctime)s]"
                "[%(levelname)s]"
                "[%(name)s] "
                "%(message)s"
            )

            # 2. Configurar el manejador exclusivo para el archivo
            file_handler = logging.FileHandler('horus.log', mode='a', encoding='utf-8')
            file_handler.setFormatter(formatter)
            
            # 3. Añadir solo el manejador de archivo al logger
            self.logger.addHandler(file_handler)

    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)

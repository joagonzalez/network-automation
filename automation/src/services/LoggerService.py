import os
import json
from config.settings import config
import logging, logging.config

class LoggerService:
    def __init__(self, path='', envvar='LOG_CFG'):
        """
        Logging loggers and handlers condifuration via logging.json file parameters
        """
        # loggerPath = envvar is not None else path
        path = 'config/logging.json'
        value = os.getenv(envvar, None)
        if value:
            path = value
        if os.path.exists(path):
            with open(path, 'rt') as f:
                log_config = json.load(f)
            logging.config.dictConfig(log_config)
        else:
            logging.basicConfig(level=logging.INFO)

        self.logger = logging.getLogger(config['LOGGER'])

    def error(self, message):
        self.logger.error(message)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)


"""
Create as loggers needed for the app
"""

loggerService = LoggerService()
#loggerServiceDebug = LoggerService()
import os
import logging
import logging.handlers
from datetime import datetime
from common.config_loader import ConfigLoader

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Logger(metaclass=SingletonMeta):
    def __init__(self, log_format='[%(asctime)s] %(name)s %(module)s %(lineno)d %(levelname)s : %(message)s', date_format='%Y-%m-%d %H:%M:%S'):
        if not hasattr(self, 'initialized'):
            self.config = ConfigLoader()
            self.system_name = self.config.get('AppName')
            self.project_home = self.config.get('project_home')
            self.separator = self.config.get_path_separator()
            self.log_dir = self.config.get('log_dir')
            self.log_file = self.config.get('logfile')
            self.log_file_path = f"{self.config.get('project_home')}{self.separator}{self.log_dir}"
            self.log_file_name = self.config.get('logfile')
            self.log_level = self.config.get('logLevel').upper()
            self.log_format = self.config.get('logformat')
            self.date_format = date_format
            self.loggers = {}
            self.initialized = True

    def get_logger(self, category):
        if category not in self.loggers:
            logger = logging.getLogger(category)
            logger.setLevel(getattr(logging, self.log_level, logging.INFO))
            formatter = logging.Formatter(self.log_format, self.date_format)

            if not os.path.exists(self.log_file_path):
                os.makedirs(self.log_file_path)

            file_handler = logging.FileHandler(rf"{self.log_file_path}{self.separator}{self.log_file_name}_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            error_file_handler = logging.FileHandler(rf"{self.log_file_path}{self.separator}error_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8')
            error_file_handler.setLevel(logging.ERROR)
            error_file_handler.setFormatter(formatter)
            logger.addHandler(error_file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            self.loggers[category] = logger
        return self.loggers[category]

    def debug(self, message, category=None):
        if category is None:
            category = self.system_name
        logger = self.get_logger(category)
        logger.debug(message)

    def info(self, message, category=None):
        if category is None:
            category = self.system_name
        logger = self.get_logger(category)
        logger.info(message)

    def warning(self, message, category=None):
        if category is None:
            category = self.system_name
        logger = self.get_logger(category)
        logger.warning(message)

    def error(self, message, exception=None, category=None):
        if category is None:
            category = self.system_name
        logger = self.get_logger(category)
        if exception:
            logger.error(f"{message}, Exception: {exception}", exc_info=True)
        else:
            logger.error(message)

    def critical(self, message, category=None):
        if category is None:
            category = self.system_name
        logger = self.get_logger(category)
        logger.critical(message)

if __name__ == "__main__":
    from common.logger import Logger
    
    logger_instance1 = Logger()
    logger_instance2 = Logger()

    print(logger_instance1 is logger_instance2)
    logger_instance1.info("This is an info log.")
    logger_instance1.error("This is an error log.")

import logging


class LoggingConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.log_instance = LoggingConfig()
        return cls._instance

    def __init__(self):
        self.error_logger = logging.getLogger('error_logger')
        self.debug_logger = logging.getLogger('debug_logger')

        # Create file handlers for each logger
        self.error_handler = logging.FileHandler('logs/error.log')
        self.debug_handler = logging.FileHandler('logs/debug.log')

        # Set logging levels
        self.error_logger.setLevel(logging.ERROR)
        self.debug_logger.setLevel(logging.DEBUG)

        # Set formatters for the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.error_handler.setFormatter(formatter)
        self.debug_handler.setFormatter(formatter)

        # Add handlers to the loggers
        self.error_logger.addHandler(self.error_handler)
        self.debug_logger.addHandler(self.debug_handler)

    def set_error_logs(self, message):
        self.error_logger.error(message, exc_info=True)

    def set_debug_logger(self, message):
        return self.debug_logger.debug(message)


import logging
import os
import sys

class Logger:
    logger = logging.getLogger()

    @staticmethod
    def setUpLogger(log_path: str = None):
        Logger.logger.setLevel(logging.DEBUG)
        fmt = '%(asctime)s | %(levelname)8s | %(message)s'

        if not os.path.exists(log_path):
            log_path = os.path.join(os.getcwd(), 'logs', 'app.log')
            os.makedirs(os.path.dirname(log_path), exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(fmt)
        file_handler.setFormatter(file_formatter)
        Logger.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        if sys.stdout.isatty():
            console_handler.setFormatter(Formatter(fmt))
        Logger.logger.addHandler(console_handler) 

class Formatter:
    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


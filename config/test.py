import logging
from logger import Logger
from config import Config
# Set up logging

# Create Config instance
config = Config('config.json')

# Set up logging
Logger.setUpLogger(config.get('log_path'))

# Get logger instance
logger = logging.getLogger(__name__)

# Log messages
logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
logger.critical('Critical message')

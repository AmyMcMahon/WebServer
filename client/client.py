from config.config import Config
from config.logger import Logger

class Application:
    def __init__(self):
        self.config = Config("config.json")
        Logger.setUpLogger(self.config.get('log_path'))
        self.logger = logging.getLogger(__name__)
        self.logger.info("Client initialized")
import logging
from config.config import Config
from config.logger import Logger
from client.laptop import LaptopMetrics

class Application:
    def __init__(self):
        self.config = Config("config.json")
        self.logger = logging.getLogger(__name__)
        self.logger.info("Client initialized")
    
    def run(self) -> int:
        try:
            self.logger.info("Client running...")
            self.collect_metrics()
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1
    
    def collect_metrics(self):
        self.logger.info("Collecting metrics...")
        laptop_metrics = LaptopMetrics()
        metrics = laptop_metrics.get_metrics()
    
    def send_metrics(self):
        self.logger.info("Sending metrics...")

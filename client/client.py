import logging
import requests
import time
from datetime import datetime, timedelta
from config.config import Config
from config.logger import Logger
from client.laptop import LaptopMetrics

class Application:
    def __init__(self):
        self.config = Config("config.json")
        self.logger = logging.getLogger(__name__)
        self.logger.info("Client initialized")
    
    def run(self, mode) -> int:
        try:
            self.logger.info("Client running...")
            self.collect_metrics(mode)
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1
    
    def collect_metrics(self, mode):
        self.logger.info("Collecting metrics...")
        if mode == "prod":
            server_url = f"http://{self.config.get('web.production.host')}:{self.config.get('web.production.port')}/upload_metrics"
        else:
            server_url = f"http://{self.config.get('web.development.host')}:{self.config.get('web.development.port')}/upload_metrics"
        headers = {'Content-Type': 'application/json'}

        try:
            interval = 10
            last_run_time = datetime.now() - timedelta(seconds=interval)

            while(True):
                time.sleep(0.5)
                current_time = datetime.now()
                if (current_time - last_run_time).total_seconds() >= interval:
                    self.logger.info("%s second timer elapsed, executing timed logic...", interval)
                    last_run_time = current_time
                    laptop_metrics = LaptopMetrics()
                metrics = laptop_metrics.get_metrics()
                if metrics is None:
                    self.logger.error("Failed to collect metrics")
                    continue    

                self.logger.info("Sending snapshot to server at %s with headers %s and json %s", server_url, headers, metrics)
                response = requests.post(server_url, data=metrics, headers=headers)
                
                if response.status_code != 201:
                    self.logger.error("Failed to upload snapshot. Server returned: %s", response.text)
                    raise Exception(f"Failed to upload snapshot. Status code: {response.status_code}")
                    
                self.logger.info("Successfully uploaded snapshot to server")
            
            self.logger.info("Application completed successfully")
            return 0
            
        except Exception as e:
            self.logger.exception("Application failed with error: %s", str(e))
            return 1
        
    def send_metrics(self):
        self.logger.info("Sending metrics...")


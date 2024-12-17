from config.config import Config
from config.logger import Logger
from client.laptop import LaptopMetrics
from datetime import datetime, timedelta
import socketio
import logging
import json
import time
import sys

class Application:
    def __init__(self):
        self.config = Config("config.json")
        self.logger = logging.getLogger(__name__)
        self.logger.info("Live Client initialized")

        if "-test" in sys.argv:
            host = self.config.get('web.development.host')
            port = self.config.get('web.development.port')
        else:
            host = self.config.get('web.production.host')
            port = self.config.get('web.production.port')
        self.url = f"http://{host}:{port}"
        self.logger.info(f"Server URL: {self.url}")

        # SocketIO client setup
        self.sio = socketio.Client()

        @self.sio.event
        def connect():
            self.logger.info("Connected to server successfully.")

        @self.sio.event
        def disconnect():
            self.logger.info("Disconnected from server.")
        
    def run(self):
        try:
            self.logger.info("Client running...")
            self.sio.connect(self.url)
            self.collect_metrics()
        except Exception as e:
            self.logger.error(f"Error: {e}")
        finally:
            self.sio.disconnect()
            self.logger.info("SocketIO disconnected.")
    
    def collect_metrics(self):
        self.logger.info("Collecting metrics...")
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
                if not metrics:
                    self.logger.error("Failed to collect metrics.")
                    continue   
                json_formatted_str = json.dumps(metrics, indent=2)
                self.sio.emit("metrics", json_formatted_str)
                self.logger.info("Metrics sent successfully.")


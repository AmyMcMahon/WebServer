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
        """ Initialize the Application class """
        self.config = Config("config.json")
        self.logger = logging.getLogger(__name__)
        self.logger.info("Live Client initialized")

        # Set the server URL based on the environment
        if "-test" in sys.argv:
            self.url = f"http://{self.config.get('web.development.host')}:{self.config.get('web.development.port')}/upload_metrics"
        else:
            self.url = f"https://webserver-6n25.onrender.com"
        
        self.logger.info(f"Server URL: {self.url}")

        # Initialize the socketio client
        self.sio = socketio.Client(logger=True, engineio_logger=True)
    
        @self.sio.event
        def connect():
            self.logger.info("Connected to server successfully.")

        @self.sio.event
        def disconnect():
            self.logger.info("Disconnected from server.")
        
    def run(self):
        """ Run the client application """
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
        """ Collect metrics from the client device """
        self.logger.info("Collecting metrics...")
        interval = 10
        last_run_time = datetime.now() - timedelta(seconds=interval)

        while(True):
            time.sleep(0.5)
            current_time = datetime.now()

            # logic executes after 10 seconds regardless of the time it takes to execute
            if (current_time - last_run_time).total_seconds() >= interval:
                self.logger.info("%s second timer elapsed, executing timed logic...", interval)
                last_run_time = current_time
                laptop_metrics = LaptopMetrics()
                metrics = laptop_metrics.get_metrics()
                if not metrics:
                    self.logger.error("Failed to collect metrics.")
                    continue   
                json_formatted_str = json.dumps(metrics, indent=2)

                # Send metrics to the server
                self.sio.emit("metrics", json_formatted_str)
                self.logger.info("Metrics sent successfully.")


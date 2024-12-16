import psutil
import logging
import platform
import json
import time

class LaptopMetrics:
    def __init__(self):
        self.devices = []
        self.name = platform.node()  
        self.logger = logging.getLogger(__name__)
        self.logger.info("LaptopMetrics initialized")

    def get_metrics(self):
        self.logger.info("Reading data from local device %s", self.name)
        try:
            # Collect the metrics
            metrics = {
                "cpu_usage_percent": psutil.cpu_percent(interval=1),
                "running_threads": sum(p.num_threads() for p in psutil.process_iter(attrs=None, ad_value=None)),
            }
            # Prepare the data in the required format
            data = {
                "devices": [
                    {
                        "name": self.name,
                        "type": "laptop",
                        "time": int(time.time()),  # Current time as a Unix timestamp
                        "metric": [
                            {
                                "name": "cpu_usage_percent",
                                "type": "percentage",
                                "value": metrics["cpu_usage_percent"]
                            },
                            {
                                "name": "running_threads",
                                "type": "count",
                                "value": metrics["running_threads"]
                            }
                        ]
                    }
                ]
            }
            
            # Log and return the data
            self.logger.info("Metrics collected successfully: %s", data)
            return json.dumps(data)  # Return as JSON string
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return None

import psutil
import logging
import platform

class LaptopMetrics:
    def __init__(self):
        self.devices = []
        self.name = platform.node()
        self.logger = logging.getLogger(__name__)
        self.logger.info("LaptopMetrics initialized")
    
    def get_metrics(self):
        self.logger.info("Reading data from local device %s", self.name)
        try:
            metrics = {
                "cpu_usage_percent": psutil.cpu_percent(interval=1),
                "running_threads": sum(p.num_threads() for p in psutil.process_iter(attrs=None, ad_value=None)),
            }
            self.logger.info("Metrics collected successfully: %s", metrics)
            return metrics
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return {
                "cpu_usage_percent": None,
                "running_threads": None,
                "error": str(e),
            }
import serial
import logging
import json
import time

class BeetleMetric:
    def __init__(self, port="COM9", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.devices = []
        self.name = "Firebeetle ESP32" 
        self.logger = logging.getLogger(__name__)
        self.logger.info("BeetleMetrics initialized")
        
        self._init_serial_connection()

    def _init_serial_connection(self):
        """Initialize serial connection."""
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.logger.info(f"Connected to {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to {self.port}: {e}")
            raise e

    def get_metrics(self):
        """Read and return metrics from serial connection."""
        if not self.serial_connection:
            self.logger.error("Serial connection not established.")
            return None
        
        try:
            self.logger.info("Reading data from device %s", self.name)
            line = self.serial_connection.readline().decode('utf-8').strip()
            self.logger.info(f"Received data: {line}")
    
            # Filter for lines containing the JSON data
            if line.startswith('{') and line.endswith('}'):
                try:
                    data_collected = json.loads(line)
                    data = {
                        "devices": [
                            {
                                "name": self.name,
                                "type": "firebeetle",
                                "time": int(time.time()),  
                                "metric": [
                                    {
                                        "name": "sound_level",
                                        "type": "count",
                                        "value": data_collected['mic_value']
                                    },
                                    {
                                        "name": "free_heap",
                                        "type": "count",
                                        "value": data_collected['second_metric']
                                    }
                                ]
                            }
                        ]
                    }
                    self.logger.info("Metrics collected successfully: %s", data)
                    return json.dumps(data)
                except json.JSONDecodeError:
                    self.logger.error("Error decoding JSON data.")
                    pass
        except Exception as e:
            self.logger.error(f"Error reading from serial port: {e}")
            self.close()
            return None

    def close(self):
        """Close the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.logger.info("Serial connection closed.")

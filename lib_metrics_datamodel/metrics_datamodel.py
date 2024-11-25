"""
Library module for the data model for the metrics data.
All data and logic to read and store metrics data from supported devices.
"""

from datetime import datetime
from typing import List
from uuid import UUID
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import logging
import psutil
import platform


@dataclass_json
@dataclass
class Metric:
    name: str
    value: float

@dataclass_json
@dataclass 
class Device:
    logger = logging.getLogger(__name__)
    name: str
        
    @staticmethod
    def read_PC_metrics() -> 'DataSnapshot':
        """Creates and returns a new DataSnapshot instance"""
        pc_device_name = platform.node()
        device = Device(name=pc_device_name)
        data_snapshot = DataSnapshot(device)

        Device.logger.info("Reading data from local device %s", device.name)
        
        num_system_threads = 0
        num_processes = 0
        for process in psutil.process_iter(['num_threads', 'name']):
            try:
                thread_count = process.num_threads()
                Device.logger.debug("Process %s(%d) has %d threads", process.name(), process.pid, thread_count)
                num_system_threads += thread_count
                num_processes += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Skip processes we can't access
                continue
        
        Device.logger.info("#System Threads: %d across %d processes", num_system_threads, num_processes)
        data_snapshot.metrics.append(Metric(name="num_system_threads", value=num_system_threads))
        data_snapshot.metrics.append(Metric(name="num_processes", value=num_processes))
   
        memory = psutil.virtual_memory()
        used_ram_mb = memory.used / (1024 * 1024)  # Convert bytes to MB
        total_ram_mb = memory.total / (1024 * 1024)
        ram_percent = memory.percent
        
        Device.logger.info("RAM Usage: %.2f MB / %.2f MB (%.1f%%)", used_ram_mb, total_ram_mb, ram_percent)
        data_snapshot.metrics.append(Metric(name="used_ram_mb", value=used_ram_mb))
        data_snapshot.metrics.append(Metric(name="total_ram_mb", value=total_ram_mb))
        data_snapshot.metrics.append(Metric(name="ram_percent", value=ram_percent))

        return data_snapshot

@dataclass_json
@dataclass
class DataSnapshot:
    logger = logging.getLogger(__name__)

    device: Device = None
    timestamp: datetime = field(default_factory=datetime.now)
    metrics: List[Metric] = field(default_factory=list)
 
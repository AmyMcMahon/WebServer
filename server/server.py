import logging
import socket
from waitress import serve
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from flask import Flask, request, jsonify
from config.config import Config
from config.logger import Logger
from db import *

class Application:
    def __init__(self):
        self.config = Config("config.json")
        self.webserver = Flask(__name__)
        self.logger = logging.getLogger(__name__)
        self.setup_routes()
        self.engine = create_engine(self.config.get('database.connection_string'))
        self.logger.info("Server initialized")
    
    def run(self, server_ip: str = "", port: int = 0) -> int:
        try:
            self.logger.info("Server running...")
            server_host = server_ip if len(server_ip) > 0 else self.config.get('web.host')
            server_port = port if port > 0 else self.config.get('web.port')
            self.logger.info(f"Starting Flask Server: {server_host}:{server_port}")
            #serve(self.webserver, host=server_host, port=server_port, _quiet=True)
            self.webserver.run(debug=server_host, port=server_port)
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1
       
    def setup_routes(self):
        """Setup the routes for the application."""
        self.webserver.route("/")(self.hello_world)
        self.webserver.route("/upload_snapshots", methods=['POST'])(self.upload_snapshot)
        self.webserver.route("/aggregators", methods=['GET', 'POST'])(self.aggregators)
        self.webserver.route("/devices", methods=['GET', 'POST'])(self.handle_devices)
        self.webserver.route("/metrics", methods=['GET'])(self.get_metrics)

    def hello_world(self):
        self.logger.info("Hello, World! route called")
        return "Hello, World!"
    
    def aggregators(self):
        self.logger.info("Aggregators route called")

    def handle_devices(self):
        self.logger.info("Devices route called")
    
    def get_metrics(self):
        self.logger.info("Get metrics route called")
    
    def upload_snapshot(self):
        self.logger.info("Upload snapshot route called")
        session = None
        try:
            if request.method == 'POST':
                data = request.json
                session = Session(self.engine)
                self.logger.info(f"Received snapshot data: {data}")
                aggregator = session.query(Aggregator).filter(Aggregator.guid == data['guid']).first()
                if not aggregator:
                    self.logger.info(f"Aggregator not found with GUID: {data['guid']}")
                    aggregator = (Aggregator(guid=data['guid'], name=data['name']))
                    session.add(aggregator)
                    session.flush()
                
            for device_data in data.get('devices', []):
                #check if the device exists - else add it in 
                device = session.query(Device).filter(Device.name == device_data['name']).first()
                if not device:
                    self.logger.info(f"Device not found with name: {device_data['name']}")
                    max_ordinal = session.query(Device).filter_by(aggregator_id=aggregator.aggregator_id).count()
                    device = Device(aggregator_id=aggregator.aggregator_id, name=device_data['name'], ordinal=max_ordinal)
                    session.add(device)
                    session.flush()

                now_UTC = datetime.now(timezone.utc)
                for metric_data in device_data.get('metrics', []):
                    #check if the metric type exists - else add it in   
                    metric_type = session.query(DeviceMetricType).filter(DeviceMetricType.name == metric_data['name']).first()
                    if not metric_type:
                        self.logger.info(f"DeviceMetricType not found with name: {metric_data['name']}")
                        metric_type = DeviceMetricType(device_id=device.device_id, name=metric_data['name'])
                        session.add(metric_type)
                        session.flush()

                    metric_snapshot = MetricSnapshot(device_id=device.device_id, client_timestamp= device_data['timestamp'], server_timestamp=int(now_UTC.timestamp()),)
                    session.add(metric_snapshot)
                    session.flush()

                    metric_value = MetricValue(metric_snapshot_id=metric_snapshot.metric_snapshot_id, device_metric_type_id=metric_type.device_metric_type_id, value=metric_data['value'])
                    session.add(metric_value)
                    session.flush() 

            session.commit()
            self.logger.info("Snapshot data saved successfully")
            session.close()

            return {
                'status': 'success',
                'message': 'Aggregator snapshot uploaded successfully'
            }, 201

        except Exception as e:
            self.logger.error(f"Error uploading snapshot: {e}")
            return {
                'status': 'error',
                'message': 'Error uploading snapshot'
            }, 500
                

app_instance = Application()
app = app_instance.webserver
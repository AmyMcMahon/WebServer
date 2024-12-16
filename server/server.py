import logging
import socket
import sys
import time
from sqlalchemy import create_engine, func
from sqlalchemy import inspect
from sqlalchemy.orm import Session, joinedload
from flask import Flask, request, jsonify, render_template
from config.config import Config
from config.logger import Logger
from db import *

class Application:
    def __init__(self):
        self.config = Config("config.json")
        self.webserver = Flask(__name__)
        self.logger = logging.getLogger(__name__)
        self.setup_routes()
        
        if "-test" in sys.argv:
            db_connection_string = self.config.get("web.development.connection_string")
            self.logger.info("Using development database connection string")
        else:
            db_connection_string = self.config.get("web.production.connection_string")
            self.logger.info("Using production database connection string")

        self.engine = create_engine(db_connection_string)
        self.logger.info("Server initialized")
    
    def run(self, server_ip: str = "", port: int = 0) -> int:
        try:
            self.logger.info("Server running...")
            server_host = server_ip if len(server_ip) > 0 else self.config.get('web.development.host')
            server_port = port if port > 0 else self.config.get('web.development.port')
            self.logger.info(f"Starting Flask Server: {server_host}:{server_port}")
            #serve(self.webserver, host=server_host, port=server_port, _quiet=True)
            self.webserver.run(debug=server_host, port=server_port)
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1
       
    def setup_routes(self):
        """Setup the routes for the application."""
        self.webserver.route("/")(self.hello_world)
        self.webserver.route("/upload_metrics", methods=['GET', 'POST'])(self.upload_metrics)
        # self.webserver.route("/devices", methods=['GET', 'POST'])(self.handle_devices)
        self.webserver.route("/metrics", methods=['GET'])(self.get_metrics)
        self.webserver.route("/esp_metrics", methods=['GET', 'POST'])(self.get_esp)

    def hello_world(self):
        self.logger.info("Hello, World! route called")
        devices = self.get_devices()
        metrics_data = self.get_metrics()
        self.logger.info("data gathered")
        return render_template("home.html", devices=devices, metrics_data=metrics_data)

    def get_devices(self):
        """Get devices from the database."""
        self.logger.info("Fetching devices from the database")
        session = Session(self.engine) 
        devices = session.query(Device).all()
        session.close()
        return devices

    def get_metrics(self):
        self.logger.info("Fetching metrics from the database")
        session = Session(self.engine)
        metrics = (session.query(Metric).options(joinedload(Metric.metric_type).joinedload(MetricType.device)).all())
        session.close()

        data = {}
        for metric in metrics:
            device_name = metric.metric_type.device.name
            metric_type_name = metric.metric_type.name
            timestamp = metric.client_timestamp
            value = metric.value

            if device_name not in data:
                data[device_name] = {}
            if metric_type_name not in data[device_name]:
                data[device_name][metric_type_name] = []

            # Append each metric's timestamp and value
            data[device_name][metric_type_name].append({"x": timestamp, "y": value})
        return data

    
    def get_metric_types(self):
        self.logger.info("Get metric types route called")
        session = Session(self.engine)
        metric_types = session.query(MetricType).all()
        session.close()
        return metric_types

    def get_esp(self):
        self.logger.info("ESP data route called")
        data = request.get_json()
        mic_value = data.get("mic_value")
        second_metric = data.get("second_metric")

        if mic_value is not None and second_metric is not None:
            self.logger.info(f"Received mic_value: {mic_value}, second_metric: {second_metric}")
            # Process the metrics as needed
        else:
            self.logger.error("Missing mic_value or second_metric in the received data")
            return jsonify({"status": "error", "message": "Invalid data format"}), 400

        return jsonify({"status": "success", "message": "Data received successfully"}), 200

    def upload_metrics(self):
        self.logger.info("Upload snapshot route called")
        data = request.get_json()
        self.logger.info("Received snapshot: %s", data)
        session = Session(self.engine)

        for device_data in data["devices"]:
            self.logger.info("Processing device %s", device_data["name"])
            db_device = session.query(Device).filter(Device.name == device_data["name"]).first()
            if db_device is None:
                db_device = Device(name=device_data["name"], device_type=device_data["type"])
                session.add(db_device)
                session.flush()
                self.logger.info("Added device %s", db_device)
            
            for metric in device_data["metric"]:
                metric_type = session.query(MetricType).filter(MetricType.name == metric["name"]).first()
                if metric_type is None:
                    metric_type = MetricType(device_id=db_device.device_id, name=metric["name"])
                    session.add(metric_type)
                    session.flush()
                    self.logger.info("Added metric type %s", metric_type)
                
                metric = Metric(metric_type_id=metric_type.metric_type_id, value=metric["value"], client_timestamp=device_data["time"], server_timestamp=int(time.time()))
                session.add(metric)
                session.flush()
                self.logger.info("Added metric %s", metric)
        
        session.commit()
        session.close()

        return {
                'status': 'success',
                'message': 'Data uploaded successfully'
            }, 201

app = Application().webserver
        
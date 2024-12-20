import eventlet
eventlet.monkey_patch()

import logging
import socket
import sys
import time
import os
from sqlalchemy import create_engine, func
from sqlalchemy import inspect
from sqlalchemy.orm import Session, joinedload
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO,send, emit,  join_room, leave_room
from config.config import Config
from config.logger import Logger
from db import *

class Application:
    def __init__(self):
        """ Initialize the application. """
        self.config = Config("config.json")
        self.webserver = Flask(__name__)
        CORS(self.webserver,resources={r"/*":{"origins":"*"}})
        self.socketio = SocketIO(self.webserver,cors_allowed_origins="*", async_mode='eventlet')
        self.connected_clients = set()
        self.logger = logging.getLogger(__name__)
        self.setup_routes()
        self.setup_socketio_handlers()
        
        #load in env variables depending on environment
        try:
            from dotenv import load_dotenv
            load_dotenv()
            self.logger.info("Loaded environment variables - dotenv")
            self.logger.info(f"Loaded environment variables: {os.getenv('EXTERNAL_DB')}")
            self.engine = create_engine(os.getenv("EXTERNAL_DB"))
        except Exception as e:
            self.logger.info("Loaded environment variables : {os.getenv('EXTERNAL_DB')}")
            self.engine = create_engine(os.environ.get("EXTERNAL_DB"))

        self.logger.info("Server initialized")
  
    def run(self, server_ip: str = "", port: int = 0) -> int:
        """Run the application."""
        try:
            self.logger.info("Server running...")
            server_host = server_ip if len(server_ip) > 0 else self.config.get('web.development.host')
            server_port = port if port > 0 else self.config.get('web.development.port')
            self.logger.info(f"Starting Flask Server: {server_host}:{server_port}")
            self.socketio.run(self.webserver, host=server_host, port=server_port)
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1
       
    def setup_routes(self):
        """Setup the routes for the application."""
        self.webserver.route("/")(self.hello_world)
        self.webserver.route("/upload_metrics", methods=['GET', 'POST'])(self.upload_metrics)
        self.webserver.route("/metrics", methods=['GET'])(self.get_metrics)

    def setup_socketio_handlers(self):
        """Setup Socket.IO event handlers."""
        @self.socketio.on('connect')
        def handle_connect():
            self.logger.info(f"Client connected: {request.sid}")
            self.connected_clients.add(request.sid)
            emit('message', 'Hello from the server!')

        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.logger.info(f"Client disconnected: {request.sid}")
            self.connected_clients.discard(request.sid)

        @self.socketio.on("metrics")
        def handle_metrics(data):
            self.logger.info(f"Received metrics: {data}")
            emit('metrics',data, broadcast=True)
            self.logger.info(f'connected_clients: {list(self.connected_clients)}')
            self.logger.info("Broadcasted metrics to all clients")

    def hello_world(self):
        """main route route."""
        self.logger.info("Hello, World! route called")
        devices = self.get_devices()
        metrics_data = self.get_metrics()
        self.logger.info("data gathered")
        server_url = request.host_url
        return render_template("home.html", devices=devices, metrics_data=metrics_data, connected_clients=self.connected_clients, server_url=server_url, cpuUsage = 0, threads = 0)

    def get_devices(self):
        """Get devices from the database."""
        self.logger.info("Fetching devices from the database")
        session = Session(self.engine) 
        devices = session.query(Device).all()
        session.close()
        return devices

    def get_metrics(self):
        """Get metrics from the database."""
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
            data[device_name][metric_type_name].append({"x": timestamp, "y": value})
        return data

    def upload_metrics(self):
        """Upload metrics to the database."""
        self.logger.info("Upload snapshot route called")
        data = request.get_json()
        self.logger.info("Received snapshot: %s", data)
        session = Session(self.engine)

        # parse JSON data and insert into database
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
        
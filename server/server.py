import logging
import socket
from flask import Flask, request, jsonify
from config.config import Config
from config.logger import Logger

class Application:
    def __init__(self):
        self.config = Config("config.json")
        self.webserver = Flask(__name__)
        self.logger = logging.getLogger(__name__)
        self.setup_routes()
        logging.basicConfig(level=logging.INFO)
        self.logger.info("Server initialized")
    
    def run(self, server_ip: str = "", port: int = 0) -> int:
        try:
            self.logger.info("Server running...")
            self.logger.debug(self.config.get('web.host'))
            self.logger.debug(self.config.get('web.port'))
            server_host = server_ip if len(server_ip) > 0 else self.config.get('web.host')
            server_port = port if port > 0 else self.config.get('web.port')
            self.logger.info(f"Starting Flask Server: {server_host}:{server_port}")
            self.webserver.run(host=server_host, port=server_port, debug=True)
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1
    
    def setup_routes(self):
        """Setup the routes for the application."""
        self.webserver.route("/")(self.hello_world)
        self.webserver.route("/metrics", methods=['GET'])(self.metrics)

    def hello_world(self):
        """Hello world route."""
        self.logger.info("Hello world route called")
        return {'message': 'Hello, World!'}

    def metrics(self):
        """Metrics route."""
        self.logger.info("Metrics route called")
        return {'message': 'Metrics route called'}

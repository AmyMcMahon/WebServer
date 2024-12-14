import argparse
import sys
import logging
import subprocess
import client.client as client
import server.server as server
from config.config import Config
from config.logger import Logger

class MainApplication:
    def __init__(self):
        self.config = Config("config.json")
        Logger.setUpLogger(self.config.get('log_path'))
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Main application initialized")

    def run(self) -> int:
        try:
            self.logger.info("Main application running...")
            parser = argparse.ArgumentParser(description='Run application in server, client or auto modes') 
            group = parser.add_mutually_exclusive_group(required=True)
            group.add_argument('-s', action='store_true', help='server mode')
            group.add_argument('-c', action='store_true', help='client mode')
            parser.add_argument("-test", action="store_true", help="Enable test mode")
            parser.add_argument("-serverip", type=str, help="IP address of the server", default=self.config.get('web.host'))
            parser.add_argument("-port", type=int, help="Port number for server/client", default=self.config.get('web.port'))

            args = parser.parse_args()
            self.logger.info(f"Arguments parsed: {args}")

            server_ip = args.serverip
            port = args.port 
            self.logger.info(f"Params given: server IP: {server_ip}, port: {port}. Config will backfill blanks.")

            app_to_run = None
            if args.s:
                self.logger.info("Running server")
                if args.test:
                    return server.Application().run(server_ip, port)
                else:
                     subprocess.run(['gunicorn', '--bind', '0.0.0.0:8000', 'server.server:app'], check=True) 
            elif args.c:
                self.logger.info("Running client")
                return client.Application().run()
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1
        

def main() -> int:
    """Entry point for the application."""
    app = MainApplication()
    return app.run()

if __name__ == "__main__":
     main()

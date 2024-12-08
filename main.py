import argparse
import sys
import logging
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
            group.add_argument('-a', action='store_true', help='auto mode')

            args = parser.parse_args()
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1
        

def main() -> int:
    """Entry point for the application."""
    app = MainApplication()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())

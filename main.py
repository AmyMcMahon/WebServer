import argparse

class MainApplication:
    def __init__(self):
       print("test")

    def run(self) -> int:
        parser = argparse.ArgumentParser(description='Run application in server, client or auto modes') 
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-s', action='store_true', help='server mode')
        group.add_argument('-c', action='store_true', help='client mode')
        group.add_argument('-a', action='store_true', help='auto mode')

        args = parser.parse_args()
        

def main() -> int:
    """Entry point for the application."""
    app = MainApplication()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())

import os
import json

class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None
        self.load_config(config_path)
    
    def load_config(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, 'r') as f:
            self.config = json.load(f)       

    def get(self, key: str, default= None):
        return self.config.get(key, default)
        
        
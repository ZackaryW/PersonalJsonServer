import json
import os
class ConfigManager:
    default_path = os.path.join(os.getcwd(), 'config.json')
    
    def __init__(self) -> None:
        self.config = self.read_config(self.default_path)
    
    def read_config(self, path: str):
        if not os.path.exists(path):
            return {}
        
        with open(path, 'r') as f:
            return json.load(f)
        
    def write_config(self, path: str=None, config: dict=None):
        if config is None:
            config = self.config
        if path is None:
            path = self.default_path
        with open(path, 'w') as f:
                
            json.dump(config, f, indent=4)
            
            
    def get_config(self, key: str, default=None):
        return self.config.get(key, default)
    
    def set_config(self, key: str, value):
        self.config[key] = value
        self.write_config(self.default_path, self.config)
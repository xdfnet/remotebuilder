import os
import yaml
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 
            'config.yaml'
        )
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self._resolve_env_vars()
        except Exception as e:
            raise RuntimeError(f"Failed to load config file: {str(e)}")
    
    def _resolve_env_vars(self) -> None:
        def _resolve_value(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                return os.environ.get(env_var, value)
            elif isinstance(value, dict):
                return {k: _resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_resolve_value(item) for item in value]
            return value
            
        self.config = _resolve_value(self.config)
    
    def get_logging_config(self) -> Dict[str, Any]:
        return self.config.get('logging', {})
    
    def get_packaging_config(self, platform: str) -> Dict[str, Any]:
        return self.config.get('packaging', {}).get(platform, {})

    def get_machines_config(self) -> Dict[str, Any]:
        return self.config.get('machines', {}) 
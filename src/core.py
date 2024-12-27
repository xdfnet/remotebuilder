import os
import sys
import time
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any, Optional, Type, Tuple, Callable
from functools import wraps

# Logger Setup
class LoggerSetup:
    @staticmethod
    def setup_logging(config: Dict[str, Any]) -> None:
        log_file = config.get('file', 'logs/packager.log')
        log_dir = os.path.dirname(log_file)
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        formatter = logging.Formatter(
            config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        root_logger = logging.getLogger()
        root_logger.setLevel(config.get('level', 'INFO'))
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.get('max_size', 10 * 1024 * 1024),
            backupCount=config.get('backup_count', 5),
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        logging.getLogger('paramiko').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        logging.info("Logging system initialized")

# Retry Decorator
def retry_operation(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logging.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed: {str(e)}. "
                            f"Retrying in {current_delay:.1f} seconds..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logging.error(
                            f"All {max_attempts} attempts failed. "
                            f"Last error: {str(e)}"
                        )
            
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator 
import logging
import os
import threading
from logging.handlers import RotatingFileHandler
from datetime import datetime


class Logger:
    """
    A unified Logger class for the Beehive application.
    Provides production-ready logging with both file and console output.
    Supports multiple log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    
    _instances = {}
    _lock = threading.Lock()
    
    def __init__(self, name: str = "beehive", log_dir: str = "logs"):
        """
        Initialize a logger instance.
        
        Args:
            name: The name of the logger (usually the module name)
            log_dir: Directory where log files will be stored (default: 'logs')
        """
        self.logger = logging.getLogger(name)
        
        # Avoid adding duplicate handlers if logger already configured
        if self.logger.handlers:
            return
        
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Define log format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File Handler - All logs (DEBUG and above)
        log_file = os.path.join(log_dir, "beehive.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5  # Keep 5 backup files
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Error Log Handler - Only errors and critical (separate file)
        error_log_file = os.path.join(log_dir, "beehive_errors.log")
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # Console Handler - INFO and above (for development/monitoring)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    @staticmethod
    def get_logger(name: str = "beehive", log_dir: str = "logs") -> 'Logger':
        """
        Get or create a logger instance (singleton pattern per name).
        
        Args:
            name: The name of the logger
            log_dir: Directory for log files
            
        Returns:
            Logger instance
        """
        if name not in Logger._instances:
            Logger._instances[name] = Logger(name, log_dir)
        return Logger._instances[name]
    
    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log an error message."""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str):
        """Log a critical message."""
        self.logger.critical(message)

 
logger = Logger.get_logger("beehive")

"""
Logging configuration module.
Sets up logging for the application with console and file outputs.
"""

import logging
import logging.config
import os
import sys
from datetime import datetime
from pathlib import Path

from .settings import get_settings


def setup_logging():
    """
    Configure logging for the application.
    Creates logs directory if it doesn't exist.
    Sets up console and file handlers.
    """
    settings = get_settings()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Generate a log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"{timestamp}_app.log"
    
    # Determine the log level based on debug mode
    log_level = "DEBUG" if settings.debug else "INFO"
    
    # Configure logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": log_level,
                "formatter": "default",
                "filename": log_file,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file"],
                "level": log_level,
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console", "file"],
                "level": "WARNING",  # Set to "INFO" to log all SQL statements
                "propagate": False,
            },
        },
    }
    
    # Apply the configuration
    logging.config.dictConfig(logging_config)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level {log_level}")
    logger.info(f"Log file: {log_file}")
    
    return logger 
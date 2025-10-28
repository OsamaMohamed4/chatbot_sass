import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pythonjsonlogger import jsonlogger

from app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging"""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add custom fields
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['environment'] = settings.ENVIRONMENT
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id


def setup_logging():
    """Configure application logging"""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(
        logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO
    )
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console Handler (with colors for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO)
    
    if settings.ENVIRONMENT == "development":
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # JSON format for production
        console_format = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # File Handler - General Application Logs
    app_file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    app_file_handler.setLevel(logging.INFO)
    app_file_handler.setFormatter(CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    ))
    root_logger.addHandler(app_file_handler)
    
    # File Handler - Error Logs
    error_file_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    ))
    root_logger.addHandler(error_file_handler)
    
    # File Handler - Access Logs (time-based rotation)
    access_file_handler = TimedRotatingFileHandler(
        log_dir / "access.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    access_file_handler.setLevel(logging.INFO)
    access_file_handler.setFormatter(CustomJsonFormatter(
        '%(timestamp)s %(level)s %(message)s'
    ))
    
    # Create access logger
    access_logger = logging.getLogger("access")
    access_logger.addHandler(access_file_handler)
    access_logger.propagate = False
    
    # Configure third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.ENVIRONMENT == "development" else logging.WARNING
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    return root_logger


# Logger instances for different purposes
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


# Specific loggers
app_logger = get_logger("app")
api_logger = get_logger("api")
db_logger = get_logger("database")
security_logger = get_logger("security")
access_logger = get_logger("access")
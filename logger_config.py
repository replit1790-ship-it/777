import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(
    log_level=logging.INFO,
    log_file="app.log",
    log_dir="logs",
    console_output=True,
):
    """
    Configure logging with both console and file handlers.
    
    Args:
        log_level: Logging level (default: logging.INFO)
        log_file: Name of the log file (default: "app.log")
        log_dir: Directory for log files (default: "logs")
        console_output: Whether to output to console (default: True)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Define log format
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    log_file_path = os.path.join(log_dir, log_file)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5  # Keep 5 backup files
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name=None):
    """
    Get a logger instance.
    
    Args:
        name: Logger name (default: None, uses module name)
    
    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        name = __name__
    return logging.getLogger(name)


# Module-level logger instance
logger = setup_logging()


if __name__ == "__main__":
    # Test logging configuration
    test_logger = setup_logging(log_level=logging.DEBUG)
    
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")
    
    print(f"\nLogs saved to: logs/app.log")

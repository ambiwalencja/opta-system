import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
import uuid
from contextvars import ContextVar

# Create a 'storage' for our Request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="n/a")

class RequestIDFilter(logging.Filter):
    """
    This filter 'injects' the current request_id into every log record.
    """
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True
    

class IgnoreWinchFilter(logging.Filter):
    """
    This filter ignores log records that contain the word 'winch' (case-insensitive) in their message.
    Signals that Gunicorn logs by default (these are usually harmless and can clutter logs)
    """
    # def filter(self, record):
    #     # We check both the raw message and the formatted message
    #     message = record.getMessage().lower()
    #     return "winch" not in message
    def filter(self, record):
        # We search the raw msg AND the args for the word 'winch'
        # Gunicorn often stores 'winch' in record.args
        msg = str(record.msg)
        args = str(record.args)
        
        if "winch" in msg.lower() or "winch" in args.lower():
            return False # Drop the log
        return True

def setup_logger():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    winch_filter = IgnoreWinchFilter()

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    gunicorn_error_logger.addFilter(winch_filter)
    logger = logging.getLogger("opta_system_logger")

    # Create a File Handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"), 
        maxBytes=10**6,  # 1MB per file
        backupCount=5    # Keep 5 old log files
    )
    
    # Create a format for the file
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(request_id)s] [%(module)s]: %(message)s'
    )
    file_handler.setFormatter(formatter)

    # Create filters and add to the handler
    rid_filter = RequestIDFilter()
    
    file_handler.addFilter(rid_filter)
    file_handler.addFilter(winch_filter)

    # Add the file handler to the logger
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        logger.addHandler(file_handler)
        
    # Sync the Gunicorn terminal handlers too
    for handler in gunicorn_error_logger.handlers:
        handler.setFormatter(formatter) 
        handler.addFilter(rid_filter)
        handler.addFilter(winch_filter)
        if handler not in logger.handlers:
            logger.addHandler(handler)
    
    logger.setLevel(gunicorn_error_logger.level)
    
    return logger


def setup_logger_daylog():
    # Ensure a logs directory exists
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    logger = logging.getLogger("my_app_logger")
    
    # Add the filter to the logger
    logger.addFilter(RequestIDFilter())

    # Create the Timed Handler
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, "app.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    
    # Add a timestamp-heavy format for the file
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(request_id)s] [%(module)s]: %(message)s'
    )
    file_handler.setFormatter(formatter)

    # Attach handlers
    if not any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers):
        logger.addHandler(file_handler)
        
    # Also attach Gunicorn's terminal handlers so you see logs in both places
    for handler in gunicorn_error_logger.handlers:
        handler.setFormatter(formatter) # Sync terminal format too
        logger.addHandler(handler)

    logger.setLevel(gunicorn_error_logger.level)

    return logger
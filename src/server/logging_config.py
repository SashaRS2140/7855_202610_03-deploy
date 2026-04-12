"""
Structured Logging Configuration for CUBE Application.
Provides JSON-formatted logging with contextual information.
"""

import logging
import json
import sys
from datetime import datetime
import os


class CustomJsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Pretty-prints in development, compact in production.
    
    Security: Filters out sensitive data to prevent accidental secret leakage.
    """
    
    # Sensitive field names that should be masked in logs
    SENSITIVE_FIELDS = {
        'token', 'jwt', 'authorization', 'x-api-key', 'api_key', 'secret',
        'password', 'passwd', 'pwd', 'apikey', 'access_token', 'refresh_token',
        'key', 'private_key', 'secret_key', 'firebase', 'credentials',
        'ip_address'
    }

    def __init__(self):
        super().__init__()
        self.is_dev = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    def _sanitize_value(self, key, value):
        # If the log field key is sensitive, replace the value with a redacted marker.
        # This prevents secrets from being written into structured logs.
        """Return sanitized value if key is sensitive, otherwise return original."""
        if isinstance(key, str) and key.lower() in self.SENSITIVE_FIELDS:
            return "[REDACTED]"
        return value

    def format(self, record):
        # Convert a Python log record into a structured JSON object.
        # Includes default fields and any additional contextual fields added by filters.
        """Format log record as JSON with context and security filtering."""
        try:
            log_obj = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'module': record.module,
                'function': record.funcName,
                'message': record.getMessage(),
            }

            # Add extra fields from the log record.
            default_record_attrs = {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                'thread', 'threadName', 'processName', 'process', 'message',
                'asctime'
            }

            for key, value in record.__dict__.items():
                if key not in default_record_attrs and not key.startswith('_'):
                    log_obj[key] = self._sanitize_value(key, value)

            # Pretty-print in development, compact in production
            return json.dumps(
                log_obj,
                indent=2 if self.is_dev else None,
                separators=(',', ':') if not self.is_dev else None,
                default=str
            )
        except Exception as e:
            # Fallback if JSON formatting fails
            return json.dumps({
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'ERROR',
                'module': 'logging_config',
                'function': 'CustomJsonFormatter.format',
                'message': f'Log formatting failed: {str(e)}',
                'original_message': record.getMessage()
            })


def setup_logging(app=None):
    # Configure the root logger and attach handlers for console and file output.
    # This must be called once at startup before any application logging occurs.
    """
    Setup structured logging for the Flask application.
    Call this early in your application initialization.
    """
    try:
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(os.getenv('LOG_LEVEL', 'DEBUG'))

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Create console handler with custom formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomJsonFormatter())
        root_logger.addHandler(console_handler)
        
        # Create file handler - write to logs/app.log
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        log_file = os.path.join(logs_dir, 'app.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(CustomJsonFormatter())
        root_logger.addHandler(file_handler)
        
        # Add RequestContextFilter to both handlers
        console_handler.addFilter(RequestContextFilter())
        file_handler.addFilter(RequestContextFilter())

        # Log initialization success
        root_logger.info("Structured logging initialized", extra={
            'app_type': os.getenv('APP_TYPE', 'web'),
            'environment': 'development' if os.getenv('FLASK_DEBUG', 'False').lower() == 'true' else 'production',
            'log_level': os.getenv('LOG_LEVEL', 'DEBUG'),
            'log_file': log_file
        })
    except Exception as e:
        # Fallback: print to stderr if logging setup fails
        print(f"CRITICAL: Logging setup failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


def get_logger(name):
    # Return a named logger instance for the current module.
    # Named loggers allow log records to be grouped by source module.
    """
    Get a logger instance with the specified name.
    Use: logger = get_logger(__name__)
    """
    return logging.getLogger(name)


class RequestContextFilter(logging.Filter):
    """
    Logging filter that adds request context to log records.
    Use in Flask request handlers to automatically add user/request info.
    """

    def filter(self, record):
        # Add Flask request-specific context to the log record when a request is active.
        # This enriches logs with endpoint, HTTP method, client IP, and optionally user_id.
        """Add request context to log record if available."""
        try:
            from flask import request, has_request_context, session

            if has_request_context():
                record.endpoint = request.endpoint or 'unknown'
                record.method = request.method
                record.ip_address = request.remote_addr
                
                # Add user_id if available in session
                if 'uid' in session:
                    record.user_id = session['uid']
                elif hasattr(request, 'user_id'):
                    record.user_id = request.user_id
        except Exception:
            # Silently ignore if request context is not available
            pass
        
        return True

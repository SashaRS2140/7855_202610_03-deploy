from flask import jsonify, request
from src.server.logging_config import get_logger

logger = get_logger(__name__)


def api_error(message, status=400, error_type=None, extra=None, log_level="warning"):
    """Return a JSON API error response and log it consistently."""
    payload = {"error": message}
    log_context = {
        "endpoint": request.path,
        "method": request.method,
        "status_code": status,
    }
    if error_type:
        log_context["error_type"] = error_type
    if extra:
        log_context.update(extra)

    log_method = getattr(logger, log_level, logger.warning)
    log_method(message, extra=log_context)

    return jsonify(payload), status

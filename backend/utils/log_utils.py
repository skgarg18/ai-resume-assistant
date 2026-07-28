import contextvars
import sys
from loguru import logger
from config.constants import LOG_DIR

# Remove default logger
logger.remove()


# ==========================================================
# Common Log Format
# ==========================================================

def dynamic_formatter(record):
    """
    Dynamically formats log records by including all
    bound context (session_id, filename, etc.) safely.
    """
    extras = [
        f"{key}={value}"
        for key, value in record["extra"].items()
        if key != "extra_str" and value not in (None, "")
    ]

    record["extra"]["extra_str"] = f" | {' | '.join(extras)}" if extras else ""

    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level>"
        "{extra[extra_str]}"
        " | {name}:{function}:{line} | "
        "{message}\n"
    )


# ==========================================================
# Console Logs
# ==========================================================

logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=False,
    format=dynamic_formatter,
)


# ==========================================================
# Application Logs
# ==========================================================

logger.add(
    LOG_DIR / "app.log",
    level="INFO",
    rotation="5 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=False,
    format=dynamic_formatter,
)


# ==========================================================
# Error Logs
# ==========================================================

logger.add(
    LOG_DIR / "error.log",
    level="ERROR",
    rotation="5 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=False,
    format=dynamic_formatter,
)


# ==========================================================
# Context Logger
# ==========================================================

default_logger = logger.bind()

_logger_context = contextvars.ContextVar(
    "request_logger",
    default=default_logger,
)


def set_logger(log):
    """Store the logger for current request/job and return token."""
    return _logger_context.set(log)


def reset_logger(token):
    """Reset context logger back to previous state."""
    _logger_context.reset(token)


def get_logger():
    """Get the logger bound to the current request/job."""
    return _logger_context.get()


def bind_logger(**kwargs):
    """
    Bind additional context (session_id, user_id, etc.)
    to the current contextvar logger.
    """
    log = get_logger().bind(**kwargs)
    set_logger(log)
    return log
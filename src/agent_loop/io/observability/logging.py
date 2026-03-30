"""Timestamped console logging for CLI output."""

import logging
from datetime import datetime

_logger = logging.getLogger("agent_loop")


def configure_logging() -> None:
    """Set up the root agent_loop logger for console output."""
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)


def log(msg: str, prefix: str = "") -> None:
    """Log a timestamped message."""
    timestamp = datetime.now().astimezone().strftime("%H:%M:%S")
    _logger.info("[%s] %s%s", timestamp, prefix, msg)


def log_blank() -> None:
    """Log a blank line to separate log sections."""
    _logger.info("")


def log_step(msg: str, *, last: bool = False) -> None:
    """Log a step under the current issue."""
    connector = "└──" if last else "├──"
    log(f"{connector} {msg}")


def log_detail(msg: str, *, last_step: bool = False) -> None:
    """Log a detail line under the current step."""
    rail = " " if last_step else "│"
    log(f"{rail}      {msg}")

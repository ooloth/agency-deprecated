"""Timestamped console logging for CLI output."""

import logging

log = logging.getLogger("agent_loop")


def configure_logging(*, verbose: bool = False) -> None:
    """Set up the agent_loop logger for timestamped console output."""
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S"))
    log.addHandler(handler)
    log.setLevel(logging.DEBUG if verbose else logging.INFO)


def log_step(msg: str, *, last: bool = False) -> None:
    """Log a step under the current issue."""
    connector = "└──" if last else "├──"
    log.info("%s %s", connector, msg)


def log_detail(msg: str, *, last_step: bool = False) -> None:
    """Log a detail line under the current step."""
    rail = " " if last_step else "│"
    log.info("%s      %s", rail, msg)

"""Structured logging configuration and utilities."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_dir: Path = Path("logs"),
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> logging.Logger:
    """
    Set up structured logging for the application.

    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to files
        log_to_console: Whether to log to console

    Returns:
        Configured root logger
    """
    # Create log directory
    log_dir.mkdir(exist_ok=True, parents=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_formatter = logging.Formatter("%(levelname)s: %(message)s")

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # File handler (detailed, all levels)
    if log_to_file:
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)

        # Error file handler (errors only)
        error_handler = logging.FileHandler(log_dir / "errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)

    # Console handler (concise, INFO and above)
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Convenience function to get logger for current module
logger = get_logger(__name__)

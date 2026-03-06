"""Path utilities for safe file operations."""

import re
from pathlib import Path
from typing import Optional


class PathValidationError(ValueError):
    """Raised when path validation fails."""

    pass


def sanitize_user_id(user_id: str) -> str:
    """
    Ensure user_id contains only safe characters.

    Prevents path traversal attacks by allowing only alphanumeric,
    underscore, and hyphen characters.

    Args:
        user_id: User identifier to sanitize

    Returns:
        Sanitized user_id

    Raises:
        PathValidationError: If user_id contains invalid characters
    """
    # Allow only alphanumeric, underscore, hyphen
    if not re.match(r"^[a-zA-Z0-9_-]+$", user_id):
        raise PathValidationError(
            f"Invalid user_id format: '{user_id}'. "
            "Only alphanumeric, underscore, and hyphen allowed."
        )

    # Prevent path traversal
    if ".." in user_id or "/" in user_id or "\\" in user_id:
        raise PathValidationError(
            f"Invalid user_id: '{user_id}' - path traversal attempt detected"
        )

    return user_id


def get_user_data_dir(user_id: str, base_dir: Path = Path("data")) -> Path:
    """
    Get the data directory for a user.

    Args:
        user_id: User identifier
        base_dir: Base data directory

    Returns:
        Path to user's data directory

    Raises:
        PathValidationError: If user_id is invalid
    """
    safe_user_id = sanitize_user_id(user_id)
    return base_dir / safe_user_id


def get_raw_log_path(user_id: str, base_dir: Path = Path("data")) -> Path:
    """
    Get the path to a user's raw event log.

    Args:
        user_id: User identifier
        base_dir: Base data directory

    Returns:
        Path to raw log file
    """
    user_dir = get_user_data_dir(user_id, base_dir)
    return user_dir / "raw" / "web_tracking_log.ndjson"


def get_summaries_dir(
    user_id: str, summary_type: str = "full", base_dir: Path = Path("data")
) -> Path:
    """
    Get the directory for user summaries.

    Args:
        user_id: User identifier
        summary_type: Type of summary ("full" or "topics")
        base_dir: Base data directory

    Returns:
        Path to summaries directory
    """
    user_dir = get_user_data_dir(user_id, base_dir)
    return user_dir / "summaries" / summary_type


def get_metadata_path(user_id: str, base_dir: Path = Path("data")) -> Path:
    """
    Get the path to a user's metadata file.

    Args:
        user_id: User identifier
        base_dir: Base data directory

    Returns:
        Path to metadata file
    """
    user_dir = get_user_data_dir(user_id, base_dir)
    return user_dir / "web_tracking_metadata.ndjson"


def get_safe_path(user_id: str, subpath: str, base_dir: Path = Path("data")) -> Path:
    """
    Get a safe path within the user's data directory.

    Prevents escaping the user directory through path traversal.

    Args:
        user_id: User identifier
        subpath: Relative path within user directory
        base_dir: Base data directory

    Returns:
        Resolved path within user directory

    Raises:
        PathValidationError: If path escapes user directory
    """
    safe_user_id = sanitize_user_id(user_id)
    user_dir = base_dir / safe_user_id

    # Resolve full path
    full_path = (user_dir / subpath).resolve()
    user_dir_resolved = user_dir.resolve()

    # Ensure result is still within user_dir
    if not str(full_path).startswith(str(user_dir_resolved)):
        raise PathValidationError(
            f"Invalid path: attempted directory traversal to {full_path}"
        )

    return full_path


def ensure_dir_exists(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        The directory path
    """
    path.mkdir(parents=True, exist_ok=True)
    return path

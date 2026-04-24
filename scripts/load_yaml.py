"""YAML config loader for the resume template."""

from pathlib import Path

import yaml

REQUIRED_TOP_KEYS = {"languages", "paths"}


def load_options(yaml_path: str) -> dict:
    """Load and validate a resume template config YAML file.

    Args:
        yaml_path: Path to the YAML file (relative or absolute).

    Returns:
        Parsed configuration as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a YAML file, is empty, or is missing
            required top-level keys.
    """
    path = Path(yaml_path)

    if path.suffix.lower() not in {".yml", ".yaml"}:
        msg = f"The input file must be a YAML file (got suffix {path.suffix!r})."
        raise ValueError(msg)

    if not path.exists():
        msg = f"The YAML file {yaml_path} does not exist."
        raise FileNotFoundError(msg)

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        msg = f"The YAML file {yaml_path} is empty."
        raise ValueError(msg)

    if not isinstance(data, dict):
        msg = f"The YAML file {yaml_path} must contain a mapping at its root."
        raise ValueError(msg)

    missing = REQUIRED_TOP_KEYS - data.keys()
    if missing:
        msg = f"Missing required top-level key(s) in {yaml_path}: {sorted(missing)}"
        raise ValueError(msg)

    if not isinstance(data["languages"], list) or not data["languages"]:
        msg = "The 'languages' key must be a non-empty list."
        raise ValueError(msg)

    if not isinstance(data["paths"], dict) or "resumes" not in data["paths"]:
        msg = "The 'paths' section must include a 'resumes' mapping."
        raise ValueError(msg)

    return data

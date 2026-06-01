"""YAML config loader for the resume template."""

from pathlib import Path

import yaml

REQUIRED_TOP_KEYS = {"languages", "paths"}

# Optional class-customisation keys. All have safe defaults applied by the
# LaTeX class itself when omitted, so they're validated only if present.
VALID_FONTS = {"sourcesans", "firasans", "latinmodern"}
VALID_DENSITIES = {"compact", "normal", "spacious"}
VALID_FONTSIZES = {10, 11, 12}


def load_options(yaml_path: str) -> dict:
    """Load and validate a resume template config YAML file.

    Args:
        yaml_path: Path to the YAML file (relative or absolute).

    Returns:
        Parsed configuration as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a YAML file, is empty, or has invalid
            values (missing required keys, or out-of-domain optional keys).
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

    _validate_optional_class_keys(data, yaml_path)

    return data


def _validate_optional_class_keys(data: dict, yaml_path: str) -> None:
    """Validate the optional `font`, `density`, `base_fontsize`, `language` keys.

    Each is allowed to be absent (class defaults apply); when present, the value
    must match the documented domain.
    """
    if "font" in data and data["font"] not in VALID_FONTS:
        msg = (
            f"Invalid 'font' value in {yaml_path}: {data['font']!r}. "
            f"Must be one of {sorted(VALID_FONTS)}."
        )
        raise ValueError(msg)

    if "density" in data and data["density"] not in VALID_DENSITIES:
        msg = (
            f"Invalid 'density' value in {yaml_path}: {data['density']!r}. "
            f"Must be one of {sorted(VALID_DENSITIES)}."
        )
        raise ValueError(msg)

    if "base_fontsize" in data and data["base_fontsize"] not in VALID_FONTSIZES:
        msg = (
            f"Invalid 'base_fontsize' value in {yaml_path}: {data['base_fontsize']!r}. "
            f"Must be one of {sorted(VALID_FONTSIZES)}."
        )
        raise ValueError(msg)

    # `language` must reference an entry in `languages[]` if provided.
    if "language" in data and data["language"] not in data["languages"]:
        msg = (
            f"'language' value {data['language']!r} in {yaml_path} is not listed "
            f"in 'languages' ({data['languages']!r})."
        )
        raise ValueError(msg)

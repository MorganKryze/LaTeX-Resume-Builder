"""Write config.tex next to each resume source, derived from options.yml.

The generated file is read by `resume.cls` via `\\InputIfFileExists{config.tex}`
and can carry: accent colour, spacing density, base font, language. Any subset
of these keys can be set in options.yml; missing ones fall through to the
class defaults (black accent, normal density, sourcesans font, en).

Hand-edit safety: the generated file's first line starts with
`% AUTO-GENERATED`. If a config.tex already exists at the target path and its
first line does NOT match this marker, the script skips it with a warning —
so users who hand-edit (e.g., on Overleaf) won't have their work overwritten.

Migration: when present, the legacy `_accent.tex` (from v1) is removed after
writing the corresponding config.tex.

CLI:
    uv run python scripts/write_config.py --config options.yml --project-root .
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.load_yaml import load_options

AUTO_GEN_MARKER = "% AUTO-GENERATED"

# YAML language names → class language codes (the `fr`/`en` arg of \setLanguage).
LANG_MAP = {"french": "fr", "english": "en"}


def build_config_content(cfg: dict, yaml_lang: str) -> str:
    """Render the config.tex body for a single resume language."""
    lines = [
        AUTO_GEN_MARKER + " by scripts/write_config.py from options.yml.",
        "% Hand edits will be overwritten on next regeneration. To customise",
        "% outside of the Python pipeline (e.g. on Overleaf), delete the",
        "% AUTO-GENERATED header above and edit freely — the script preserves",
        "% any config.tex whose first line does not start with this marker.",
        "",
    ]

    accent = cfg.get("accent_color")
    if accent is not None:
        _validate_accent(accent)
        r, g, b = accent
        lines.append(f"\\definecolor{{resumeAccent}}{{RGB}}{{{r},{g},{b}}}")

    if "density" in cfg:
        lines.append(f"\\setSpacingDensity{{{cfg['density']}}}")

    if "font" in cfg:
        lines.append(f"\\setBaseFont{{{cfg['font']}}}")

    class_lang = LANG_MAP.get(yaml_lang, yaml_lang)
    lines.append(f"\\setLanguage{{{class_lang}}}")

    return "\n".join(lines) + "\n"


def _validate_accent(accent: object) -> None:
    if not isinstance(accent, list) or len(accent) != 3:
        msg = f"accent_color must be a 3-item RGB list; got {accent!r}"
        raise ValueError(msg)
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in accent):
        msg = f"accent_color components must be integers in [0, 255]; got {accent!r}"
        raise ValueError(msg)


def safe_to_write(path: Path) -> bool:
    """Return True if path is absent or starts with the AUTO-GENERATED marker."""
    if not path.exists():
        return True
    try:
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
    except (IndexError, OSError):
        return False
    return first_line.startswith(AUTO_GEN_MARKER)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write config.tex next to each declared resume source.",
    )
    parser.add_argument("--config", default="options.yml")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    cfg = load_options(args.config)

    for lang in cfg["languages"]:
        rel = cfg["paths"]["resumes"][lang]
        tex = project_root / rel
        if not tex.exists():
            raise FileNotFoundError(f"Source .tex not found: {tex}")

        config_path = tex.parent / "config.tex"
        legacy_accent = tex.parent / "_accent.tex"

        if safe_to_write(config_path):
            content = build_config_content(cfg, lang)
            config_path.write_text(content, encoding="utf-8")
            print(f"→ {config_path}")
        else:
            print(
                f"⚠ Skipping {config_path}: hand-edited file present "
                "(remove the AUTO-GENERATED header marker to allow overwriting)."
            )

        # Remove legacy v1 file if present (config.tex now supersedes it).
        if legacy_accent.exists():
            legacy_accent.unlink()
            print(f"🗑 Removed legacy {legacy_accent}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Write _accent.tex next to each resume source, derived from accent_color.

The generated file contains a single `\\definecolor{resumeAccent}{RGB}{R,G,B}`
line. The template's `style/resume.sty` does `\\IfFileExists{_accent.tex}{...}`,
so when this script runs before LaTeX compile the resume picks up the user's
chosen accent. With no generated file (or missing accent_color), the template
falls back to its built-in default (black).

CLI:
    uv run python scripts/write_accent.py --config options.yml --project-root .
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.load_yaml import load_options


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write _accent.tex next to each declared resume source.",
    )
    parser.add_argument("--config", default="options.yml")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    cfg = load_options(args.config)

    accent = cfg.get("accent_color")
    if accent is None:
        print("write_accent: no accent_color in config; skipping (template default applies).")
        return 0
    if not isinstance(accent, list) or len(accent) != 3:
        msg = f"accent_color must be a 3-item RGB list; got {accent!r}"
        raise ValueError(msg)
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in accent):
        msg = f"accent_color components must be integers in [0, 255]; got {accent!r}"
        raise ValueError(msg)

    r, g, b = accent
    line = f"\\definecolor{{resumeAccent}}{{RGB}}{{{r},{g},{b}}}\n"

    for lang in cfg["languages"]:
        rel = cfg["paths"]["resumes"][lang]
        tex = project_root / rel
        if not tex.exists():
            raise FileNotFoundError(f"Source .tex not found: {tex}")
        out = tex.parent / "_accent.tex"
        out.write_text(line, encoding="utf-8")
        print(f"→ {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

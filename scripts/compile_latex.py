"""Compile all resumes declared in the YAML config with latexmk.

CLI:
    uv run python scripts/compile_latex.py --config options.yml --project-root .
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.load_yaml import load_options


def build_latexmk_command(tex_file: Path, output_dir: Path) -> list[str]:
    """Build the latexmk command for a single .tex file."""
    return [
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={output_dir}",
        str(tex_file),
    ]


def compile_one(tex_file: Path, output_dir: Path) -> None:
    """Compile a single LaTeX file. Raises CalledProcessError on failure."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = build_latexmk_command(tex_file, output_dir)
    print(f"→ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    # latexmk writes to output_dir/<stem>.pdf; copy next to source so merge step finds it.
    built = output_dir / f"{tex_file.stem}.pdf"
    target = tex_file.with_suffix(".pdf")
    if built.resolve() != target.resolve():
        target.write_bytes(built.read_bytes())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile resume LaTeX files.")
    parser.add_argument("--config", default="options.yml")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    cfg = load_options(args.config)
    build_dir = project_root / cfg["paths"].get("build_dir", "build")

    for lang in cfg["languages"]:
        rel = cfg["paths"]["resumes"][lang]
        tex = project_root / rel
        if not tex.exists():
            raise FileNotFoundError(f"Source .tex not found: {tex}")
        compile_one(tex, build_dir)

    print(f"Compiled {len(cfg['languages'])} resume(s) → {build_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

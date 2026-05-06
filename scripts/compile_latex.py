"""Compile all resumes declared in the YAML config with latexmk.

CLI:
    uv run python scripts/compile_latex.py --config options.yml --project-root .
    uv run python scripts/compile_latex.py --config options.yml --project-root . --docker
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.load_yaml import load_options

DEFAULT_DOCKER_IMAGE = "ghcr.io/xu-cheng/texlive-full:latest"


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


def build_latexmk_docker_command(
    tex_file: Path,
    output_dir: Path,
    project_root: Path,
    image: str = DEFAULT_DOCKER_IMAGE,
) -> list[str]:
    """Build a `docker run` invocation that compiles tex_file inside the texlive-full image.

    The container mounts project_root at /work, cd's to the .tex file's parent directory
    inside the container (so relative \\usepackage{../...} paths resolve the same way
    they do in CI), and writes outputs to the absolute path inside the container that
    maps to output_dir on the host.

    On POSIX hosts a `--user` mapping is added so generated files aren't root-owned.
    """
    project_root = project_root.resolve()
    tex_rel = tex_file.resolve().relative_to(project_root)
    out_rel = output_dir.resolve().relative_to(project_root)
    work_dir = "/work"
    container_cwd = f"{work_dir}/{tex_rel.parent}".rstrip("/")
    container_out = f"{work_dir}/{out_rel}"

    # The default image (xu-cheng/texlive-full) only ships linux/amd64. Forcing the
    # platform makes Apple Silicon and other arm64 hosts emulate it (Rosetta / QEMU)
    # so the bits match what CI produces on its amd64 runners.
    cmd = ["docker", "run", "--rm", "--platform", "linux/amd64"]
    if hasattr(os, "geteuid"):
        cmd += ["--user", f"{os.geteuid()}:{os.getegid()}"]
    cmd += [
        "-e",
        "HOME=/tmp",
        "-v",
        f"{project_root}:{work_dir}",
        "-w",
        container_cwd,
        image,
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={container_out}",
        tex_rel.name,
    ]
    return cmd


def compile_one(
    tex_file: Path,
    output_dir: Path,
    *,
    use_docker: bool = False,
    docker_image: str = DEFAULT_DOCKER_IMAGE,
    project_root: Path | None = None,
) -> None:
    """Compile a single LaTeX file. Raises CalledProcessError on failure."""
    output_dir.mkdir(parents=True, exist_ok=True)
    if use_docker:
        if project_root is None:
            raise ValueError("project_root is required for Docker builds.")
        cmd = build_latexmk_docker_command(tex_file, output_dir, project_root, docker_image)
    else:
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
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Compile inside the xu-cheng/texlive-full Docker image (no local TeX needed).",
    )
    parser.add_argument(
        "--docker-image",
        default=DEFAULT_DOCKER_IMAGE,
        help="Override the Docker image used for compilation.",
    )
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    cfg = load_options(args.config)
    build_dir = project_root / cfg["paths"].get("build_dir", "build")

    for lang in cfg["languages"]:
        rel = cfg["paths"]["resumes"][lang]
        tex = project_root / rel
        if not tex.exists():
            raise FileNotFoundError(f"Source .tex not found: {tex}")
        compile_one(
            tex,
            build_dir,
            use_docker=args.docker,
            docker_image=args.docker_image,
            project_root=project_root if args.docker else None,
        )

    print(f"Compiled {len(cfg['languages'])} resume(s) → {build_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# LaTeX-Resume-Builder

> A minimal, ATS-friendly LaTeX resume template with an auto-published preview via GitHub Pages. Designed to be **forked for your own CV** or **consumed as a git submodule** from a private repo that holds your personal content.

![Resume cover](https://morgankryze.github.io/LaTeX-Resume-Builder/resume.jpg)

## What this repo is

- `style/resume.sty` — the LaTeX package (packages, margins, commands).
- `examples/resume-{en,fr}.tex` — a dummy Jane Doe resume using the package.
- `scripts/` — Python utilities (LaTeX compile driver, PDF→JPG, PDF merge, QR code generator).
- `Makefile` — one-shot entrypoints for local build (`make all`) and testing (`make test lint`).
- `.github/workflows/ci.yml` — compiles the dummy, publishes the PDF + JPEG cover to `gh-pages`.

## What this repo is NOT

It is **not** where your personal CV lives. No personal data is committed here. To put your own content in, see one of the two usage modes below.

## Quickstart (local dummy build)

```bash
git clone https://github.com/MorganKryze/LaTeX-Resume-Builder.git
cd LaTeX-Resume-Builder
make install    # sets up a uv-managed .venv from pyproject.toml + uv.lock
make all        # compile LaTeX → convert → merge → QR
ls build/       # resume-en.pdf, resume-fr.pdf, resume.pdf, qr-code.png
```

Requires: [uv](https://docs.astral.sh/uv/) (Python 3.11+ auto-provisioned), TeX Live (`latexmk`, `pdflatex`), `poppler` (`pdftoppm`).

## Usage modes

### Mode 1 — Fork as a starter template

Best if you want a **public** CV repo.

1. Click **Use this template** on GitHub.
2. Edit `examples/resume-en.tex` and `examples/resume-fr.tex` with your content.
3. Replace `assets/logo.jpg` with your own avatar.
4. Copy `options.example.yml` → `options.yml` and update `resume_url`.
5. Push — CI compiles and publishes to your own `gh-pages`.

### Mode 2 — Submodule from a private repo (recommended)

Best if you want to **keep your personal content private** while still benefiting from template upgrades.

See [`docs/SUBMODULE.md`](docs/SUBMODULE.md) for the full guide. In short:

```bash
# in your private repo
git submodule add https://github.com/MorganKryze/LaTeX-Resume-Builder.git template
# ... create content/resume-en.tex that does \usepackage{../template/style/resume}
# ... create options.yml pointing at content/
make -C template build CONFIG=../options.yml PROJECT_ROOT=..
```

## Documentation

- [`docs/USAGE.md`](docs/USAGE.md) — installation per OS, YAML schema reference, adding a new language, troubleshooting.
- [`docs/SUBMODULE.md`](docs/SUBMODULE.md) — private-repo consumption guide, step-by-step.
- [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) — LaTeX style conventions, Python linting, PR checklist.
- [`CHANGELOG.md`](CHANGELOG.md) — release notes.

## Derived from

- [jakegut/resume](https://github.com/jakegut/resume)
- [sb2nov/resume](https://github.com/sb2nov/resume) (original)

## License

MIT — see [`LICENSE`](LICENSE).

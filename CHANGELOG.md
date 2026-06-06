# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Maintenance policy.** This file is touched only at release time. Entries for
> the next version are derived from `git log <previous-tag>..HEAD`, then curated
> and grouped under the Keep a Changelog headings (Security, Fixed, Added,
> Changed, Removed, Deprecated). Do not append entries in feature PRs; the diff
> and the commit history are the source of truth between releases.

## [2.1.0] — 2026-06-05

Minor release. Adds optional **local-only personal fields** so details like a phone number can appear in a locally-built PDF without ever entering version control or a public build.

### Added

- `style/resume.cls`: declares an empty `\resumePhone` default and loads an optional `private.tex` next to each `.tex` source via `\InputIfFileExists{private.tex}{}{}`. `\resumeHeader` renders `\resumePhone` (underlined, between email and LinkedIn) when set, and nothing when empty — so CI, a fresh clone, and the published PDF stay clean while a local build picks it up.
- `private.example.tex`: commented starter documenting the `private.tex` workflow and how to add further private fields.
- `docs/USAGE.md` §4: new "`private.tex` (local-only personal fields)" subsection; the `\resumeHeader` row notes the `\resumePhone` slot.

## [2.0.2] — 2026-06-02

Patch release. Richer, prettier Jane Doe dummies to give first-time users a representative starting point. No code changes.

### Changed

- `examples/resume-en.tex` and `examples/resume-fr.tex`: punched-up Jane Doe persona — KPI-loaded bullets with `\hl{}` highlights (10k req/s, 40% latency reduction, 1k+ PyPI downloads, etc.), and a `\resumeEducationNote` demonstrating the capstone macro.
- Examples now use the `spacious` class option for an aerated layout that fills one page comfortably — also doubles as in-place documentation for the density toggle.
- Skills section uses the new `skillsTable` environment with 6 categories (Backend, Infrastructure & DevOps, Data & Databases, Observability & SRE, Tools & Practices, Soft Skills) instead of the v1 `itemize`-based block.

### Added

- `examples/config.tex`: ships a bordeaux red (`#722F37`) accent so first impressions of the template aren't black-on-white. Demonstrates the LaTeX-only customisation flow (no Python pipeline needed).

## [2.0.1] — 2026-06-01

Patch release. Fixes the v2.0.0 CI breakage on `xu-cheng/latex-action`: the workspace inside the Docker container isn't mounted at `/github/workspace` but at the runner's actual workspace path (e.g. `/home/runner/work/<repo>/<repo>`). Hardcoding the absolute path in `TEXINPUTS` broke class lookup. Replaced by a relative path (`../style/:`) that works regardless of the container's mount layout, since `work_in_root_file_dir: true` puts cwd in `examples/` (or `content/` downstream).

### Fixed

- `.github/workflows/ci.yml`: `TEXINPUTS` now uses `../style/:` instead of `/github/workspace/style/:`. Fixes `! LaTeX Error: File 'resume.cls' not found.` on every CI run.

## [2.0.0] — 2026-06-01

Major refactor: the template ships as a **LaTeX document class** (`.cls`) instead of a style package (`.sty`), and the styling decisions that used to leak into user content files are now encapsulated in dedicated macros. Configuration is centralised in a single hand-editable `config.tex` (regenerated from `options.yml` by the Python pipeline when present, edited directly on Overleaf when not).

### **BREAKING**

- `style/resume.sty` removed. Replaced by `style/resume.cls`. User `.tex` files must use `\documentclass[<opts>]{resume}` instead of `\documentclass{article}` + `\usepackage{../style/resume}`. See [`docs/MIGRATION.md`](docs/MIGRATION.md) for the v1 → v2 diff.
- `scripts/write_accent.py` renamed to `scripts/write_config.py`. It now generates a full `config.tex` (not just `_accent.tex`) carrying accent colour, spacing density, base font, and language.
- `_accent.tex` removed. `config.tex` next to each `.tex` source is the new single user-facing LaTeX config file. The script cleans up any leftover `_accent.tex` from v1 automatically.
- `Makefile` target `accent` renamed to `config`.

### Added

- `style/resume.cls` — LaTeX class with class options (`fr|en`, `compact|normal|spacious`, `10pt|11pt|12pt`), runtime setters (`\setSpacingDensity`, `\setBaseFont`, `\setLanguage`), and density-aware vertical spacing.
- New public macros: `\resumeHeader`, `\resumeTagline`, `\resumeEducationNote`, `skillsTable` environment + `\skillRow`. These replace the raw `\begin{center}…\end{center}`, raw `\begin{tabular}…\end{tabular}`, and manual `\vspace`+`\small` blocks that were copy-pasted into user `.tex` files in v1.
- `config.example.tex` — fully commented starter for the user-side overrides.
- `.latexmkrc` (consumer/template root): prepends `style/` (or `template/style/`) to `TEXINPUTS` so Overleaf-style compilations from the project root find `resume.cls` without manual env tweaks.
- `docs/MIGRATION.md`: v1 → v2 upgrade guide.
- New `options.yml` keys (all optional): `font`, `density`, `base_fontsize`, `language`. Validated by `scripts/load_yaml.py`. Missing keys fall through to class defaults.

### Changed

- `scripts/compile_latex.py`: sets `TEXINPUTS` for both local and Docker invocations so `\documentclass{resume}` resolves regardless of cwd.
- `examples/resume-{en,fr}.tex`: refactored to use the new class and macros. Same rendered PDFs.
- `docs/USAGE.md`, `docs/OVERLEAF.md`, `docs/ATS.md`: rewritten around the `.cls` + `config.tex` model.

### Removed

- `style/resume.sty`, `scripts/write_accent.py`, all `_accent.tex` references.

## [1.1.0] — 2026-05-06

Maintenance release. Fixes a CI breakage on TeX Live 2026, addresses a known-vulnerable transitive dependency, hardens the GitHub Actions supply chain, and reorganizes the documentation around four explicit usage paths (Fork, Submodule, Overleaf, Raw).

### Security

- Migrate from `PyPDF2` (unmaintained) to `pypdf >= 5.0.0`. `PyPDF2 >= 2.2.0, <= 3.0.1` is vulnerable to an infinite-loop DoS on crafted PDFs ([GHSA-hbfs-7qfc-x29r](https://github.com/py-pdf/pypdf/security/advisories/GHSA-hbfs-7qfc-x29r)). `scripts/convert_and_merge.py` now uses `pypdf.PdfWriter` (the API replacement for the deprecated `PdfMerger`).

### Fixed

- CI LaTeX compile: set `work_in_root_file_dir: true` on `xu-cheng/latex-action` so `\usepackage{../style/resume}` resolves correctly. Previous setting compiled from the workspace root and failed on TeX Live 2026 with `File '../style/resume.sty' not found`. The downstream "move PDFs" step is no longer needed and was removed.
- `pdf_to_jpg` now always writes page 1 to `<base>.jpg` regardless of total page count; additional pages go to `<base>-page2.jpg`, `<base>-page3.jpg`, … Previously single-page output was `<base>.jpg` but multi-page output was `<base>0.jpg`, which silently broke the artifact upload (`if-no-files-found: error`) for any resume that grew past one page.

### Added

- `docs/OVERLEAF.md`: end-to-end Overleaf onboarding guide. Documents the `\usepackage{../style/resume}` path gotcha (Overleaf compiles from the project root, so `..` escapes the project) and offers two working layouts (flat single-resume; folders preserved with EN+FR in one project).

### Changed

- README restructured around a four-path decision table: Fork (public CV repo), Submodule (private), Overleaf (browser-only), Raw (just the `.sty`). Each path lists its minimum-viable steps inline and links to the deep-dive doc.
- All GitHub Actions in `.github/workflows/ci.yml` are now pinned to commit SHAs (with the human-readable tag in a trailing comment) instead of floating major-version tags. Affects: `actions/checkout`, `astral-sh/setup-uv`, `xu-cheng/latex-action`, `actions/upload-artifact`, `actions/download-artifact`, `peaceiris/actions-gh-pages`.
- Documentation prose cleaned up across `README.md`, `docs/USAGE.md`, `docs/SUBMODULE.md`, `docs/OVERLEAF.md`, `docs/CONTRIBUTING.md`.

## [1.0.0] — 2026-04-24

Initial release of the LaTeX-Resume-Builder template as a **pure template** with
CI-driven build. The LaTeX style is extracted into a standalone package, Python
scripts are refactored into config-driven CLIs, and a dummy Jane Doe resume
demonstrates usage.

### Added

- `style/resume.sty` — LaTeX style package (replaces the former `src/config.tex`).
- `examples/resume-en.tex` / `resume-fr.tex` — Jane Doe dummy content.
- `scripts/compile_latex.py` — YAML-driven `latexmk` wrapper.
- `scripts/convert_and_merge.py` — CLI (`--config`, `--project-root`).
- `scripts/generate_qr_code.py` — CLI (`--config`, `--project-root`).
- `scripts/load_yaml.py` — extended schema validation (required `paths` block).
- `options.example.yml` — full example config with inline comments.
- `Makefile` — `install/build/merge/qr/test/lint/clean/all` targets, overridable `CONFIG` and `PROJECT_ROOT`.
- `pyproject.toml` + `uv.lock` — reproducible Python environment via [uv](https://docs.astral.sh/uv/).
- `assets/logo.jpg` — dummy Jane Doe monogram.
- `.github/workflows/ci.yml` — three-job pipeline: `lint-test`, `build-pdf`, `publish-gh-pages`.
- `tests/resources/sample.pdf` — tiny PDF fixture so tests no longer depend on a committed compiled resume.
- Documentation: `README.md`, `docs/USAGE.md`, `docs/SUBMODULE.md`, `docs/CONTRIBUTING.md`.

### Changed

- Repository layout reorganized for clarity: `style/`, `examples/`, `scripts/`, `assets/`, `docs/`, `site/`, `tests/`.
- The gh-pages source moved from `docs/` to `site/` (so `docs/` can be reserved for markdown documentation).
- Compiled PDFs, JPEGs, and QR images are **no longer committed** — they are generated by CI or by `make all` locally.
- Python deps declared in `pyproject.toml` (PEP 621) and locked in `uv.lock`, replacing `requirements.txt`.

### Removed

- `src/` directory (contents moved per above).
- Committed compiled artifacts: `output/resume.pdf`, `output/qr-code.png`, `src/resume-{en,fr}/resume.pdf`, `src/resume-{en,fr}/resume.jpg`, `docs/pdf/resume.pdf`, `src/downloads/*`.
- Personal content — the template ships Jane Doe only.

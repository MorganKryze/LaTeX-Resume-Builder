# Usage Guide

Reference for installing, configuring, and building with the LaTeX-Resume-Builder template.

---

## 1. Install prerequisites

### macOS

```bash
# uv (Python package & project manager; provisions its own Python)
brew install uv

# LaTeX (full recommended, ~4 GB; or basic-latex + add packages as needed)
brew install --cask mactex-no-gui      # or: brew install basictex

# Poppler (for pdf2image)
brew install poppler
```

### Linux (Debian/Ubuntu)

```bash
# uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# LaTeX + poppler
sudo apt-get update
sudo apt-get install -y \
    texlive-latex-recommended texlive-fonts-recommended texlive-latex-extra latexmk \
    poppler-utils
```

### Linux (Arch)

```bash
sudo pacman -S uv texlive-most poppler
```

### Windows

Use **WSL2** with Ubuntu, then follow the Linux instructions. Native Windows with MiKTeX also works but is harder to script reliably.

### Verify

```bash
uv --version
latexmk --version
pdflatex --version
pdftoppm -v                  # from poppler
```

`uv` auto-provisions a Python 3.11 interpreter on the first `uv sync`, so a separate Python install isn't required.

---

## 2. Install Python dependencies

```bash
uv sync            # creates .venv, resolves pyproject.toml, writes uv.lock
# or
make install
```

`uv.lock` pins exact versions, so the same packages install in every environment.

---

## 3. Build locally

```bash
make all              # compile + convert + merge + QR
make build            # only compile LaTeX
make merge            # only merge + JPG
make qr               # only QR
make test lint        # unit tests + ruff/black
make clean            # remove build artifacts
```

Outputs land in `build/` (gitignored). Each language's PDF also gets placed next to its `.tex` source so the merge step can find it.

---

## 4. Configuration (`options.yml` / `options.example.yml`)

Full schema:

```yaml
# List of language keys. Each must have a matching entry under paths.resumes.
# The merged PDF is assembled in this order.
languages:
  - english
  - french

# Source for the logo at the center of the QR code.
# Local path (resolved from --project-root) OR http(s) URL.
image_source: assets/logo.jpg

# RGB triple for the colored elements of the QR code.
color_panel: [233, 167, 135]

# URL encoded into the QR code (what people reach by scanning it).
resume_url: https://example.com/resume

# All paths are resolved relative to --project-root (default: current dir).
paths:
  resumes:
    english: examples/resume-en.tex
    french: examples/resume-fr.tex
  build_dir: build # where compiled PDFs land
  merged_pdf: build/resume.pdf # final merged output
  qr_output: build/qr-code.png # QR code PNG
  docs_pdf: site/pdf/resume.pdf # OPTIONAL: copy merged PDF here too
```

**All keys under `paths` are paths relative to `--project-root`.** Leave `docs_pdf` unset if you don't want gh-pages publication.

---

## 5. Adding a new language

1. Create `examples/resume-es.tex` (or wherever) using `\usepackage{../style/resume}`.
2. Add an entry under `paths.resumes`:

   ```yaml
   paths:
     resumes:
       english: examples/resume-en.tex
       french: examples/resume-fr.tex
       spanish: examples/resume-es.tex
   ```

3. Add the key to `languages`:

   ```yaml
   languages: [english, french, spanish]
   ```

4. No Python code changes needed.

---

## 6. CLI reference

All scripts accept the same flags. Run them through `uv run` so they use the locked environment:

```bash
uv run python scripts/compile_latex.py      --config options.yml --project-root .
uv run python scripts/convert_and_merge.py  --config options.yml --project-root .
uv run python scripts/generate_qr_code.py   --config options.yml --project-root .
```

- `--config` (default `options.yml`): path to the YAML config.
- `--project-root` (default `.`): root for resolving relative paths from the YAML.

---

## 7. Troubleshooting

### `latexmk: command not found`

Install TeX Live (see step 1). On macOS with `basictex` you may need `sudo tlmgr install latexmk`.

### `! LaTeX Error: File 'X.sty' not found.`

A package used by `style/resume.sty` isn't installed. On TeX Live:

```bash
sudo tlmgr install <package-name>
```

Or install the "full" TeX Live distribution.

### `pdf2image.exceptions.PDFInfoNotInstalledError`

`poppler` is not on PATH. On macOS: `brew install poppler`. On Linux: `apt install poppler-utils`.

### QR code generator fails on fetching a remote image

Check the `image_source` URL returns a valid image. Fall back to a local path if the remote is flaky.

### Build succeeds but the merged PDF is in the wrong language order

Reorder the `languages` list in your config.

### `make test` passes locally but fails in CI

CI runs ruff + black. Run `make lint` locally before pushing.

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

### Build via Docker (no local TeX Live)

If you don't want a 4 GB local TeX Live install, compile inside the same Docker image CI uses:

```bash
make build-docker     # latex compile in ghcr.io/xu-cheng/texlive-full
make all-docker       # build-docker + merge + qr
```

Requirements: Docker (`docker version` should respond), `uv`, and `poppler` for the merge step. The image is ~5 GB and pulled the first time you run; subsequent builds reuse the cache.

Behind the scenes, `compile_latex.py --docker` runs:

```bash
docker run --rm --platform linux/amd64 --user <uid>:<gid> -e HOME=/tmp \
  -v "<project-root>:/work" \
  -w "/work/<dir-of-tex-file>" \
  ghcr.io/xu-cheng/texlive-full:latest \
  latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -output-directory=/work/<build-dir> <tex-filename>
```

Notes:

- The container `cd`s into the `.tex` parent directory so co-located inputs (like `config.tex`) resolve the same way they do in CI. `TEXINPUTS` is set inside the container so `\documentclass{resume}` finds the class.
- `--platform linux/amd64` is always set because the upstream image only ships amd64. On Apple Silicon (M1/M2/M3) Docker Desktop runs it under Rosetta 2; first compile is slow (~minute) but cached afterwards, and output is byte-identical to CI.
- `--user` keeps generated files owned by your host user (POSIX only; ignored on Windows).
- On Linux arm64 hosts (Raspberry Pi, arm64 servers) you'll need `qemu-user-static` and `binfmt_misc` registered: `docker run --rm --privileged tonistiigi/binfmt --install all`.

---

## 4. Configuration (`options.yml` / `config.tex`)

Configuration lives in **two complementary files**:

- **`options.yml`** — single source of truth for the build pipeline (Python).
  Drives which resumes compile, the QR target, paths, the accent colour, and
  the class-level toggles (font, density, language). Read by every script.
- **`config.tex`** — LaTeX-side overrides. The class does
  `\InputIfFileExists{config.tex}{}{}` next to each `.tex` source. Generated
  automatically from `options.yml` by `scripts/write_config.py`, but can be
  hand-edited on Overleaf (or anywhere) without the Python pipeline.

### `options.yml` schema

```yaml
# List of language keys. Each must have a matching entry under paths.resumes.
# The merged PDF is assembled in this order.
languages:
  - english
  - french

# Source for the logo at the center of the QR code.
# Local path (resolved from --project-root) OR http(s) URL.
image_source: assets/logo.jpg

# Single source of truth for the accent color across the resume PDF
# (section rules, hyperlinks), the QR code eyes, and the gh-pages
# download button. RGB triple.
accent_color: [15, 55, 120]

# URL encoded into the QR code (what people reach by scanning it).
resume_url: https://example.com/resume

# --- Optional class-level customisation (since v2.0) ---
# Each key is optional; class defaults apply when omitted. When set, the
# Python pipeline emits the corresponding setter call into config.tex.
font: sourcesans            # sourcesans | firasans | latinmodern   (default: sourcesans)
density: normal             # compact | normal | spacious           (default: normal)
base_fontsize: 11           # 10 | 11 | 12                          (default: 11)
language: english           # key from `languages` above            (default: languages[0])

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

### `config.tex` (hand-editable)

Generated by `make config` (or `scripts/write_config.py`) next to each
resume source. Contains any subset of:

```latex
\definecolor{resumeAccent}{RGB}{15,55,120}
\setSpacingDensity{normal}      % compact | normal | spacious
\setBaseFont{sourcesans}        % sourcesans | firasans | latinmodern
\setLanguage{fr}                % fr | en
```

The Python pipeline writes a `% AUTO-GENERATED` header on the first line.
**To customise without Python (e.g. on Overleaf), delete that header line
and edit freely** — the script preserves any file whose first line does
not start with `% AUTO-GENERATED`.

See [`config.example.tex`](../config.example.tex) for a fully commented
starter file.

### Class macros API

Authored in your `.tex` source. All defined in `style/resume.cls`.

| Macro                                                | Purpose                                                                                                                          |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `\documentclass[<opts>]{resume}`                     | Load the class. Options: `fr`/`en`, `compact`/`normal`/`spacious`, `10pt`/`11pt`/`12pt`.                                         |
| `\resumeHeader{name}{email}{linkedin}{github}`       | Centred header block. `linkedin`/`github` are host+path without scheme (e.g. `linkedin.com/in/jdoe`); macro prepends `https://`. |
| `\resumeTagline{text}`                               | Bold-small paragraph under the header. Short pitch / target role / availability.                                                 |
| `\section{Name}`                                     | Section title with right-aligned horizontal rule.                                                                                |
| `\resumeSubHeadingListStart` / `…End`                | Wrap a list of `\resumeSubheading` / `\resumeProjectHeading` entries.                                                            |
| `\resumeSubheading{title}{dates}{org}{location}`     | Two-row entry: title + right-aligned dates; subtitle + right-aligned location.                                                   |
| `\resumeProjectHeading{title-with-stack}{dates}`     | One-row project header. Pass `\href{...}{\textbf{Name}} $\vert$ \emph{stack}` as `title-with-stack`.                             |
| `\resumeItemListStart` / `…End`                      | Wrap a list of `\resumeItem` bullets inside a subheading.                                                                        |
| `\resumeItem{text}`                                  | One bullet.                                                                                                                      |
| `\resumeEducationNote{text}`                         | Capstone / projet-fin-de-cursus annotation between `\resumeSubheading` calls. Label auto-localised by `\setLanguage`.            |
| `\begin{skillsTable} \skillRow{}{} … \end{skillsTable}` | Two-column skills/competences table. `\skillRow{label}{comma-separated content}`. Labels coloured in `resumeAccent`.           |
| `\hl{text}`                                          | Inline bold emphasis (numbers, keywords). Use sparingly.                                                                         |
| `\setSpacingDensity{compact\|normal\|spacious}`       | Override density at preamble time (from `config.tex`).                                                                           |
| `\setBaseFont{sourcesans\|firasans\|latinmodern}`     | Override base body font (from `config.tex`).                                                                                     |
| `\setLanguage{fr\|en}`                                | Override babel language + localised labels (from `config.tex`).                                                                  |

---

## 5. Adding a new language

1. Create `examples/resume-es.tex` (or wherever) using `\documentclass[es,11pt]{resume}`. (If `es` isn't a defined class option yet, fall back to `\documentclass[11pt]{resume}` and call `\setLanguage{...}` from `config.tex`.)
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
uv run python scripts/compile_latex.py      --config options.yml --project-root . --docker
uv run python scripts/convert_and_merge.py  --config options.yml --project-root .
uv run python scripts/generate_qr_code.py   --config options.yml --project-root .
```

- `--config` (default `options.yml`): path to the YAML config.
- `--project-root` (default `.`): root for resolving relative paths from the YAML.
- `--docker` (compile_latex only): run latexmk inside `ghcr.io/xu-cheng/texlive-full:latest` instead of using a local install.
- `--docker-image` (compile_latex only): override the Docker image (default `ghcr.io/xu-cheng/texlive-full:latest`).

---

## 7. Troubleshooting

### `latexmk: command not found`

Install TeX Live (see step 1). On macOS with `basictex` you may need `sudo tlmgr install latexmk`.

### `! LaTeX Error: File 'resume.cls' not found.`

The class lives in `style/resume.cls`, but `\documentclass{resume}` only looks on TeX's search path. Four ways to make it discoverable, ranked by robustness:

1. **Symlink the class next to your `.tex`** (recommended for editor/IDE workflows that bypass latexmk):
   ```bash
   cd content/        # or wherever your .tex lives
   ln -s ../template/style/resume.cls resume.cls
   ```
   Works with any compiler (pdflatex, latexmk, xelatex, etc.) since LaTeX finds the class in cwd. The symlink follows the submodule pin automatically.
2. **`.latexmkrc` in the `.tex` directory** sets `TEXINPUTS`. Works for any tool that invokes `latexmk`. Shipped by default in the consumer repo's `content/.latexmkrc`.
3. **`.latexmkrc` at project root** for Overleaf and root-level invocations.
4. **Manual env var**: `TEXINPUTS=./template/style/: pdflatex resume-fr.tex` before invoking the compiler.

`scripts/compile_latex.py` (via `make build`) already handles option 4 automatically.

### `! LaTeX Error: File 'X.sty' not found.`

A package used by `style/resume.cls` isn't installed. On TeX Live:

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

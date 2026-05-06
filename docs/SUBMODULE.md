# Using LaTeX-Resume-Builder as a git submodule

This pattern keeps your personal CV content in a private repo and delegates styling, build, and CI to the public template. Personal data stays out of the public repo, and template upgrades land in your private repo on demand.

Every command in this guide assumes you are at the root of your private repo (`my-cv/`) unless a comment says otherwise.

## Final layout

```plain
my-cv/                               # your PRIVATE repo
├── .github/
│   └── workflows/
│       └── build.yml                # private CI (Step 7, optional)
├── .gitignore
├── .gitmodules                      # written by `git submodule add` in Step 2
├── template/                        # git submodule → LaTeX-Resume-Builder (public)
├── content/
│   ├── resume-en.tex                # your actual EN resume (private)
│   └── resume-fr.tex                # your actual FR resume (private)
├── assets/
│   └── logo.jpg                     # your avatar (embedded in the QR code)
├── options.yml                      # your personal config
├── Makefile                         # thin wrapper that delegates to the submodule
└── build/                           # generated artifacts (gitignored)
```

---

## Step 1: create the private repo

```bash
mkdir my-cv && cd my-cv
git init
git remote add origin git@github.com:yourname/my-cv.git   # private
```

You should now be inside `my-cv/`. All subsequent commands run from here.

---

## Step 2: add this template as a submodule

```bash
# from my-cv/
git submodule add https://github.com/MorganKryze/LaTeX-Resume-Builder.git template
git submodule update --init --recursive
```

This creates `my-cv/template/` and writes `my-cv/.gitmodules`. The submodule is pinned to the upstream `main` HEAD at the moment you run this; bump it later via Step 8.

---

## Step 3: scaffold your directories

```bash
# from my-cv/
mkdir -p content assets
```

Drop your avatar into `assets/logo.jpg` (any square JPG/PNG; recommended ~512×512). For example:

```bash
cp ~/Pictures/me.jpg assets/logo.jpg
```

---

## Step 4: write your resume content

Create `my-cv/content/resume-en.tex`:

```bash
# from my-cv/
cat > content/resume-en.tex <<'EOF'
\documentclass[letterpaper,11pt]{article}
\usepackage{../template/style/resume}
\begin{document}

\begin{center}
  \textbf{\Huge Your Name} \\ \vspace{1pt}
  \href{mailto:you@yourdomain.com}{\underline{you@yourdomain.com}} $|$
  \href{https://linkedin.com/in/you}{\underline{linkedin.com/in/you}} $|$
  \href{https://github.com/you}{\underline{github.com/you}}
\end{center}

\section{Experience}
  \resumeSubHeadingListStart
    \resumeSubheading{Senior Engineer}{Jan. 2024 -- Present}{Your Company}{City}
    \resumeItemListStart
      \resumeItem{What you did}
    \resumeItemListEnd
  \resumeSubHeadingListEnd

\end{document}
EOF
```

Then open `content/resume-en.tex` in your editor and replace the placeholders. The available LaTeX commands (`\resumeSubheading`, `\resumeItem`, `\resumeSubHeadingListStart`, etc.) are defined in `template/style/resume.sty`.

For a French (or other) version, copy the file and translate:

```bash
# from my-cv/
cp content/resume-en.tex content/resume-fr.tex
$EDITOR content/resume-fr.tex
```

Keep the `\usepackage{../template/style/resume}` line as-is in every language file. The `..` walks one level up out of `content/` and into `template/style/`.

---

## Step 5: write `options.yml`

Create `my-cv/options.yml`:

```bash
# from my-cv/
cat > options.yml <<'EOF'
languages:
  - english
  - french

image_source: assets/logo.jpg
color_panel: [233, 167, 135]
resume_url: https://yourdomain.com/resume

paths:
  resumes:
    english: content/resume-en.tex
    french: content/resume-fr.tex
  build_dir: build
  merged_pdf: build/resume.pdf
  qr_output: build/qr-code.png
EOF
```

If you only want one language, drop `french` from `languages` and from `paths.resumes`. Full schema reference: [`USAGE.md`](USAGE.md#4-configuration-optionsyml--optionsexampleyml).

---

## Step 6: write the wrapper `Makefile`

Create `my-cv/Makefile`:

```bash
# from my-cv/
cat > Makefile <<'EOF'
TEMPLATE := template
CONFIG   := options.yml
ROOT     := .

.PHONY: all build merge qr clean

all: build merge qr

build:
	$(MAKE) -C $(TEMPLATE) build  CONFIG=../$(CONFIG) PROJECT_ROOT=../$(ROOT)

merge:
	$(MAKE) -C $(TEMPLATE) merge  CONFIG=../$(CONFIG) PROJECT_ROOT=../$(ROOT)

qr:
	$(MAKE) -C $(TEMPLATE) qr     CONFIG=../$(CONFIG) PROJECT_ROOT=../$(ROOT)

clean:
	$(MAKE) -C $(TEMPLATE) clean
	rm -rf build/
EOF
```

> **Important:** Make recipes require **tabs**, not spaces. The `cat <<'EOF'` form preserves whatever your shell emits, so check the file with `cat -A Makefile | head` if you hit `*** missing separator. Stop.` errors. The `^I` markers are tabs. Editors that auto-convert tabs to spaces will break `make`.

---

## Step 7: write `.gitignore`

```bash
# from my-cv/
cat > .gitignore <<'EOF'
# Build artifacts
build/

# Per-language compiled outputs (latexmk, xu-cheng/latex-action)
content/*.pdf
content/*.jpg
content/*.aux
content/*.log
content/*.out
content/*.toc
content/*.fls
content/*.fdb_latexmk
content/*.synctex.gz

# Editor / OS
.DS_Store
*.swp
.idea/
.vscode/

# Python (if you ever add a top-level pyproject)
.venv/
__pycache__/
EOF
```

---

## Step 8: build

```bash
# from my-cv/
make -C template install   # uv sync inside the submodule (one-time)
make all                   # compile + merge + QR
```

Outputs land in `my-cv/build/`:

- `build/resume-en.pdf`, `build/resume-fr.pdf` (per-language PDFs)
- `build/resume.pdf` (merged in `languages` order)
- `build/qr-code.png`

### No-TeX-Live alternative: build via Docker

If you don't want a local TeX Live install, swap `make all` for `make all-docker`:

```bash
# from my-cv/
make all-docker            # latex compile happens inside ghcr.io/xu-cheng/texlive-full
```

Requires Docker, `uv`, and `poppler` on `$PATH`. The image is ~5 GB on first pull (cached afterwards). The merge and QR steps still run locally via Python; only LaTeX is containerized. Same image and flags as CI, so output is byte-identical to what gets published.

---

## Step 9: first commit

```bash
# from my-cv/
git add .gitignore .gitmodules Makefile options.yml content/ assets/ template
git commit -m "chore: scaffold private resume repo with template submodule"
git push -u origin main
```

`git add template` records the **submodule pin** (the SHA), not the submodule contents. Files inside `template/` belong to the upstream repo.

---

## Step 10: updating the template

When the template ships improvements (CI fixes, style tweaks, new commands), bump the pin:

```bash
# from my-cv/
cd template
git fetch origin
git checkout main           # or a release tag, e.g. git checkout v1.1.0
git pull
cd ..
make all                    # sanity-check the build still works
git add template
git commit -m "deps: bump template to <short-sha>"
git push
```

To pin to a specific release instead of tracking `main`:

```bash
# from my-cv/
cd template && git fetch --tags && git checkout v1.1.0 && cd ..
git add template && git commit -m "deps: pin template to v1.1.0"
```

To inspect the current pin:

```bash
# from my-cv/
git submodule status                       # shows the pinned SHA
cd template && git log -1 --oneline        # what that SHA actually is
```

---

## Invariants to respect

- **Don't edit files inside `template/`** from your private repo. Anything you change there will be overwritten by the next `git pull` inside the submodule, and won't reach upstream. Open a PR against [LaTeX-Resume-Builder](https://github.com/MorganKryze/LaTeX-Resume-Builder) instead.
- **Don't hardcode paths in scripts.** Drive everything through `options.yml`.
- **`options.yml` paths must reflect your actual layout** (`content/resume-*.tex`), not the template's `examples/` layout.
- **Don't commit a dirty submodule.** If `git submodule status` shows `+<sha>` (modified), reset before committing — see "Resetting a dirty submodule" below.

### Resetting a dirty submodule

```bash
# from my-cv/
cd template
git status                  # see what changed
git restore .               # discard tracked changes
git clean -fd               # remove untracked files (careful)
git checkout <pinned-sha>   # if HEAD also drifted
cd ..
```

---

## Step 11 (optional): private CI

Mirror the template's CI in your private repo so every push compiles your real CV. The template's own CI publishes the dummy Jane Doe — your private CI publishes you.

Create `my-cv/.github/workflows/build.yml`:

```bash
# from my-cv/
mkdir -p .github/workflows
cat > .github/workflows/build.yml <<'EOF'
name: Build resume

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: build-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
        with:
          submodules: recursive
          fetch-depth: 1

      - uses: astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86 # v5.4.2
        with:
          enable-cache: true

      - name: Install system dependencies
        run: sudo apt-get update && sudo apt-get install -y poppler-utils

      - name: Sync Python dependencies
        run: make -C template install

      - name: Compile LaTeX
        uses: xu-cheng/latex-action@e2f99d4b3685b0da93f97e1b86ad8fab81105098 # v3 (3.3.0)
        with:
          root_file: |
            content/resume-en.tex
            content/resume-fr.tex
          work_in_root_file_dir: true

      - name: Merge PDFs and generate JPEG cover
        run: make merge

      - name: Generate QR code
        run: make qr

      - name: Upload build artifact
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2
        with:
          name: resume
          path: |
            build/
            content/resume-en.jpg
            content/resume-fr.jpg
          if-no-files-found: error
EOF
```

Adjust the `root_file:` and `path:` lists to match the languages you actually ship.

### How it works

- `submodules: recursive` on checkout pulls `template/` at the SHA your repo pins.
- `make -C template install` runs `uv sync` inside `template/` against `template/uv.lock`.
- The LaTeX compile step runs inside a TeX Live container (Docker), so the runner doesn't need `apt install texlive-full` (which takes ~5 minutes).
- `make merge` and `make qr` delegate into the template's scripts via the wrapper `Makefile` from Step 6.

The artifact is downloadable from the workflow run page for 90 days.

### Optional: publish to a private gh-pages

If your account allows GitHub Pages on private repos (Pro/Team/Enterprise), append this job to `build.yml`:

```yaml
publish-gh-pages:
  needs: build
  runs-on: ubuntu-latest
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  permissions:
    contents: write
  steps:
    - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
    - uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093 # v4.3.0
      with:
        name: resume
        path: artifact/
    - name: Assemble site/
      run: |
        mkdir -p site/pdf
        cp artifact/build/resume.pdf site/pdf/resume.pdf
        cp artifact/content/resume-en.jpg site/resume.jpg
    - uses: peaceiris/actions-gh-pages@4f9cc6602d3f66b9c108549d475ec49e8ef4d45e # v4.0.0
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./site
        publish_branch: gh-pages
```

> **GitHub Pages on private repos** requires a paid plan (Pro / Team / Enterprise). On a free account this job will succeed but the `gh-pages` branch won't actually serve. If you only need the PDF, stop after the `build` job — the artifact is enough.

### Optional: attach to a release

If you'd rather attach the merged PDF to a tagged release (works on free accounts), add a third job triggered on `push: tags: ['v*']`:

```yaml
release:
  needs: build
  runs-on: ubuntu-latest
  if: startsWith(github.ref, 'refs/tags/v')
  permissions:
    contents: write
  steps:
    - uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093 # v4.3.0
      with:
        name: resume
        path: artifact/
    - uses: softprops/action-gh-release@01570a1f39cb168c169c802c3bceb9e93fb10974 # v2.1.0
      with:
        files: |
          artifact/build/resume.pdf
          artifact/content/resume-en.jpg
```

Then `git tag v2026.05 && git push --tags` triggers a release with the PDF attached.

### Action SHA pinning

All the SHAs above are pinned commits, not floating tags. Keep them up to date by checking each action's release page and bumping the SHA + the `# vX.Y.Z` comment together. Avoid `@main` or `@v4` in production workflows — a compromised tag retroactively rewrites your CI.

# Using LaTeX-Resume-Builder as a git submodule

This pattern keeps your personal CV content in a private repo and delegates styling, build, and CI to the public template. Personal data stays out of the public repo, and template upgrades land in your private repo on demand.

## Final layout

```plain
my-cv/                               # your PRIVATE repo
├── template/                        # git submodule → LaTeX-Resume-Builder (public)
├── content/
│   ├── resume-en.tex                # your actual EN resume (private)
│   └── resume-fr.tex                # your actual FR resume (private)
├── assets/
│   └── logo.jpg                     # your avatar
├── options.yml                      # your personal config
├── Makefile                         # small wrapper that delegates to the submodule
└── pyproject.toml                   # optional, or just rely on template/uv.lock
```

## Step 1: create the private repo

```bash
mkdir my-cv && cd my-cv
git init
git remote add origin git@github.com:yourname/my-cv.git   # private
```

## Step 2: add this template as a submodule

```bash
git submodule add https://github.com/MorganKryze/LaTeX-Resume-Builder.git template
git submodule update --init --recursive
```

## Step 3: create your content

Create `content/resume-en.tex`:

```latex
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
```

Create `content/resume-fr.tex` the same way. Drop your avatar into `assets/logo.jpg`.

## Step 4: create your `options.yml`

```yaml
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
```

## Step 5: create your `Makefile`

```makefile
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
```

## Step 6: build

```bash
make -C template install   # uv sync inside the submodule
make all                   # compile your own content
```

Outputs land in `./build/`.

## Step 7: updating the template

When the template gets improvements:

```bash
cd template && git pull origin main && cd ..
git add template && git commit -m "Bump template to <new-sha>"
git push
```

Your personal content stays where it is. Only the pinned submodule SHA moves forward.

## Invariants to respect

- Don't edit files inside `template/` from your private repo. Contribute upstream instead.
- Don't hardcode paths in scripts. Drive them through `options.yml`.
- Your `options.yml` must reflect your actual content structure, not the template's `examples/` layout.

## Private CI (optional)

You can add a `.github/workflows/build.yml` in your private repo that mirrors the template CI against your content. The template's own CI publishes the dummy; your private CI publishes your real CV (to a private gh-pages or an S3 bucket, for example).

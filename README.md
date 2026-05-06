# LaTeX-Resume-Builder

> A minimal, ATS-friendly LaTeX resume template. One LaTeX style, one Python build pipeline, one GitHub Action that publishes a live preview to GitHub Pages.

![Resume cover](https://morgankryze.github.io/LaTeX-Resume-Builder/resume.jpg)

---

## Pick your path

Four ways to use this template. Pick what fits and jump to that section.

| You want…                                                           | Path                                          | Effort   |
| ------------------------------------------------------------------- | --------------------------------------------- | -------- |
| 🍴 A **public** CV repo you control end-to-end                      | [**Fork**](#1-fork-public-cv-repo)            | ~3 steps |
| 🔒 Your CV **private** while still tracking template upgrades       | [**Submodule**](#2-submodule-private-cv-repo) | ~5 steps |
| ☁️ Write in **Overleaf**, no local toolchain                        | [**Overleaf**](#3-overleaf-browser-only)      | ~4 steps |
| 📄 Just the `.sty` and a `.tex` starter to drop into your own setup | [**Raw**](#4-raw-just-the-files)              | ~2 steps |

If you can't decide, pick **Fork**. You can migrate to Submodule later without losing work.

---

## 1. Fork: public CV repo

Best when your CV source can be public and you want the CI + GitHub Pages preview.

1. Click **Use this template** → create your own repo.
2. Edit `examples/resume-en.tex` and `examples/resume-fr.tex` with your content. Replace `assets/logo.jpg` with your avatar.
3. Copy `options.example.yml` → `options.yml` and update `resume_url`.
4. Push. CI compiles both languages and publishes the merged PDF + cover JPEG to your `gh-pages` branch.

**Build locally** (optional):

```bash
make install   # provisions a uv-managed .venv
make all       # compile, convert, merge, QR
```

You'll need [uv](https://docs.astral.sh/uv/), TeX Live (`latexmk`, `pdflatex`), and `poppler` (`pdftoppm`). Per-OS install steps live in [`docs/USAGE.md`](docs/USAGE.md).

---

## 2. Submodule: private CV repo

Best when your CV must stay private but you want template improvements (style fixes, CI updates) for free.

```bash
mkdir my-cv && cd my-cv
git init
git submodule add https://github.com/MorganKryze/LaTeX-Resume-Builder.git template
```

Create `content/resume-en.tex` (your private content) with `\usepackage{../template/style/resume}`, plus an `options.yml` pointing at `content/`. A 4-line wrapper `Makefile` delegates everything to the submodule:

```makefile
all: ; $(MAKE) -C template all CONFIG=../options.yml PROJECT_ROOT=..
```

Personal data stays in your private repo. Pulling template upgrades is `cd template && git pull`. Full step-by-step in [`docs/SUBMODULE.md`](docs/SUBMODULE.md).

---

## 3. Overleaf: browser-only

Best when you don't want to install LaTeX locally and don't need the Python pipeline (PDF merge, QR code, gh-pages). You get the style and the resume.

1. **New Project → Blank Project** in Overleaf.
2. Upload `style/resume.sty` to the project root.
3. Upload `examples/resume-en.tex` (or `-fr.tex`) and rename it to `main.tex`.
4. Open `main.tex`, change line 8 from `\usepackage{../style/resume}` to `\usepackage{resume}`. Recompile.

Full reasoning, the alternate folder layout, and how to compile both EN+FR in one project: [`docs/OVERLEAF.md`](docs/OVERLEAF.md).

---

## 4. Raw: just the files

Best when you want the LaTeX style only and will compile in your own editor (TeXShop, VSCode + LaTeX Workshop, TeXstudio, command-line `pdflatex`).

1. Download `style/resume.sty` and one of `examples/resume-{en,fr}.tex`.
2. Place both in the same directory, change `\usepackage{../style/resume}` → `\usepackage{resume}`, compile.

You give up the multi-language PDF merge, the QR code, and the auto-published preview. The resume itself compiles fine.

---

## What's in the box

```plain
LaTeX-Resume-Builder/
├── style/resume.sty           # the LaTeX package: packages, margins, commands
├── examples/                  # dummy "Jane Doe" resumes in EN + FR
├── scripts/                   # Python utilities (compile, merge, QR)
│   ├── compile_latex.py       # latexmk driver
│   ├── convert_and_merge.py   # PDF→JPG + multi-language merge
│   └── generate_qr_code.py    # QR code with embedded logo
├── options.example.yml        # config schema (paths, languages, QR color)
├── Makefile                   # one-shot entrypoints (make all / test / lint)
└── .github/workflows/ci.yml   # builds + publishes to gh-pages
```

Each script is single-purpose, all paths come from `options.yml`, and the Makefile only delegates.

---

## Documentation

| Doc                                            | When to read                                                                   |
| ---------------------------------------------- | ------------------------------------------------------------------------------ |
| [`docs/USAGE.md`](docs/USAGE.md)               | Per-OS install, YAML schema, adding a language, CLI reference, troubleshooting |
| [`docs/SUBMODULE.md`](docs/SUBMODULE.md)       | Setting up the private-repo + submodule pattern end-to-end                     |
| [`docs/OVERLEAF.md`](docs/OVERLEAF.md)         | Overleaf upload layouts, the `\usepackage` path gotcha, EN+FR in one project   |
| [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) | LaTeX style conventions, Python lint rules, PR checklist                       |
| [`CHANGELOG.md`](CHANGELOG.md)                 | Release notes                                                                  |

---

## Derived from

- [jakegut/resume](https://github.com/jakegut/resume)
- [sb2nov/resume](https://github.com/sb2nov/resume) (original)

## License

MIT. See [`LICENSE`](LICENSE).

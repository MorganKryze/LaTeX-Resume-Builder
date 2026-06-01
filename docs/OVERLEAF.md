# Using LaTeX-Resume-Builder on Overleaf

From "I have an Overleaf account" to "my CV compiles" in 4 steps. You won't run any of the Python tooling: Overleaf provides LaTeX, you provide content.

You get the class, the resume layout, and full edit-and-recompile in the browser. You don't get the multi-language PDF merge, the QR code generator, the auto-published GitHub Pages preview, or CI. Those rely on the Python pipeline that Overleaf doesn't run.

---

## The path gotcha (v2+)

The class file `resume.cls` lives in `style/` and the dummy `.tex` files in `examples/` load it with:

```latex
\documentclass[en,11pt]{resume}
```

`\documentclass{...}` only looks for `resume.cls` on TeX's search path, **not** in a relative directory. Two ways to satisfy that on Overleaf:

- **Layout A (flat)** — put `resume.cls` at the same level as your `.tex`. LaTeX finds it in the current directory. Simplest, recommended.
- **Layout B (folders preserved)** — keep `style/resume.cls` and use a `.latexmkrc` at project root that prepends `style/` to `TEXINPUTS`. Already shipped at the project root of this repo, so you just upload it.

Pick the one that matches how many resumes you want in the project.

---

## Layout A: flat (one resume, simplest)

Best when you only need one language, or you want to keep two separate Overleaf projects (one per language).

### Steps

1. **Create project**: in Overleaf, click **New Project → Blank Project**, name it whatever.
2. **Upload the class**: from this repo, grab [`style/resume.cls`](../style/resume.cls). In Overleaf, click **Upload** and drop it in the project root.
3. **Upload the resume**: grab [`examples/resume-en.tex`](../examples/resume-en.tex) (or `-fr.tex`). Upload it to the project root and either rename it `main.tex` or set it as the main document under **Menu → Main document**.
4. **(Optional) Upload `config.tex`** alongside it if you want to override the accent colour, density, font, or language. Use [`config.example.tex`](../config.example.tex) as a starter.
5. **Recompile**.

### Final layout in Overleaf

```plain
your-project/
├── main.tex           # the resume (uses \documentclass{resume})
├── resume.cls         # the class, sitting next to it
└── config.tex         # (optional) overrides
```

---

## Layout B: folders preserved (EN + FR in one project)

Best when you want both language versions side by side and prefer the upstream folder structure.

### Steps

1. **Create project**: **New Project → Blank Project**.
2. **Recreate the folders**: in Overleaf, click **New Folder**, create `style/` and `examples/`.
3. **Upload**:
   - `style/resume.cls` → into the `style/` folder
   - `examples/resume-en.tex` → into `examples/`
   - `examples/resume-fr.tex` → into `examples/`
   - `.latexmkrc` (from this repo's root) → into the project root
4. **Set the main document**: **Menu → Main document → examples/resume-en.tex** (or `-fr.tex`). Switch which one is "main" to compile the other language.
5. **(Optional) Add a `config.tex`** next to each `.tex` you compile (so `examples/config.tex`) — or just one at the project root, the class falls back to the cwd.

### Final layout in Overleaf

```plain
your-project/
├── .latexmkrc                  # prepends style/ to TEXINPUTS
├── style/
│   └── resume.cls
└── examples/
    ├── resume-en.tex
    ├── resume-fr.tex
    └── config.tex              # (optional) overrides
```

The shipped `.latexmkrc` does:

```perl
$ENV{'TEXINPUTS'} = './style/:' . ($ENV{'TEXINPUTS'} || '');
```

Overleaf reads `.latexmkrc` from the project root before invoking `latexmk`, so the class is found regardless of which `.tex` is the main document.

> **Note:** Overleaf compiles one main document at a time. To produce a merged EN+FR PDF you'd need the local pipeline (`make all`). Overleaf doesn't run the Python merge step.

---

## Customising without Python

Edit `config.tex` directly. None of these need the Python pipeline:

```latex
\definecolor{resumeAccent}{HTML}{0F3778}   % section rules, links, labels
\setSpacingDensity{compact}                % compact | normal | spacious
\setBaseFont{firasans}                     % sourcesans | firasans | latinmodern
\setLanguage{fr}                           % fr | en
```

The class does `\InputIfFileExists{config.tex}{}{}` next to each `.tex` source, so a missing file is fine — the defaults apply.

If you imported a `config.tex` that starts with `% AUTO-GENERATED` from the Python pipeline, **delete that first line** before hand-editing. Otherwise a future `make config` run would overwrite your changes (only relevant if you go back to local).

See [`config.example.tex`](../config.example.tex) for a fully commented starter.

---

## Adding your content

Once the project compiles, edit the `.tex` file in place. The class provides these commands (defined in `style/resume.cls`):

- `\resumeHeader{name}{email}{linkedin}{github}` — centred header block
- `\resumeTagline{text}` — bold-small pitch paragraph below the header
- `\resumeSubHeadingListStart` / `\resumeSubHeadingListEnd` wrap a list of jobs, projects, or education entries
- `\resumeSubheading{Title}{Date}{Org}{Location}` is one entry header
- `\resumeProjectHeading{title-with-stack}{dates}` is one project header
- `\resumeItemListStart` / `\resumeItemListEnd` wrap bullet points under an entry
- `\resumeItem{...}` is one bullet point
- `\begin{skillsTable} \skillRow{Label}{content} … \end{skillsTable}` is the skills / compétences block
- `\resumeEducationNote{text}` is the localised capstone annotation between education entries
- `\hl{text}` is inline bold emphasis for KPIs and keywords

The dummy resume shows every command in context. Full API in [USAGE.md §4](USAGE.md#4-configuration-optionsyml--configtex).

---

## Troubleshooting

### `! LaTeX Error: File 'resume.cls' not found.`

The class isn't where LaTeX is looking.

- Layout A: check `resume.cls` is at the project root, not inside a folder.
- Layout B: check `.latexmkrc` is at the project root and `style/resume.cls` exists under `style/`. Re-recompile after uploading `.latexmkrc` (Overleaf reads it once at compile start).

### `! LaTeX Error: File 'X.sty' not found` (something other than `resume.cls`)

A package required by `resume.cls` isn't in Overleaf's TeX Live image. Overleaf ships TeX Live full by default, so this is rare. If it happens, switch the project's TeX Live version under **Menu → Settings → TeX Live version** to the latest.

### Fonts look different from the GitHub Pages preview

Overleaf and the GitHub Action both use TeX Live full, so output should match. If it doesn't, check the **Compiler** setting (Menu → Settings). The template targets `pdfLaTeX`.

### I want CI / auto-publishing

Overleaf doesn't run GitHub Actions. For automated preview, use [Mode 1 (Fork)](../README.md#1-fork-public-cv-repo) or [Mode 2 (Submodule)](../README.md#2-submodule-private-cv-repo). Overleaf alone is editor-only.

---

## Going back to local

If you want PDF merge, QR codes, or CI later, copy your edited `.tex` back into a fork of this repo: drop it in `examples/`, and run `make all`. The class is already there; nothing to patch.

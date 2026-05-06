# Using LaTeX-Resume-Builder on Overleaf

From "I have an Overleaf account" to "my CV compiles" in 4 steps. You won't run any of the Python tooling: Overleaf provides LaTeX, you provide content.

You get the style, the resume layout, and full edit-and-recompile in the browser. You don't get the multi-language PDF merge, the QR code generator, the auto-published GitHub Pages preview, or CI. Those rely on the Python pipeline that Overleaf doesn't run.

---

## The path gotcha

The dummy `.tex` files live in `examples/` and load the style with a relative parent path:

```latex
\usepackage{../style/resume}
```

This works when LaTeX runs from `examples/` and finds the style one directory up. Overleaf compiles from the project root, so `../style/resume` resolves to outside your Overleaf project and fails with `File '../style/resume.sty' not found`.

Fix it with one of two layouts. Pick the one that matches how many resumes you want in the project.

---

## Layout A: flat (one resume, simplest)

Best when you only need one language, or you want to keep two separate Overleaf projects (one per language).

### Steps

1. **Create project**: in Overleaf, click **New Project → Blank Project**, name it whatever.
2. **Upload the style**: from this repo, grab [`style/resume.sty`](../style/resume.sty). In Overleaf, click **Upload** and drop it in the project root.
3. **Upload the resume**: grab [`examples/resume-en.tex`](../examples/resume-en.tex) (or `-fr.tex`). Upload it to the project root and rename it `main.tex` (or set it as the main document under **Menu → Main document**).
4. **Patch the `\usepackage`**: open `main.tex` and change line 8:

   ```diff
   - \usepackage{../style/resume}
   + \usepackage{resume}
   ```

5. **Recompile**.

### Final layout in Overleaf

```plain
your-project/
├── main.tex           # the resume
└── resume.sty         # the style, sitting next to it
```

---

## Layout B: folders preserved (EN + FR in one project)

Best when you want both language versions side by side and prefer to keep the upstream folder structure.

### Steps

1. **Create project**: **New Project → Blank Project**.
2. **Recreate the folders**: in Overleaf, click **New Folder**, create `style/` and `examples/`.
3. **Upload**:
   - `style/resume.sty` → into the `style/` folder
   - `examples/resume-en.tex` → into `examples/`
   - `examples/resume-fr.tex` → into `examples/`
4. **Patch both `.tex` files**, line 8:

   ```diff
   - \usepackage{../style/resume}
   + \usepackage{style/resume}
   ```

   Drop the `..`. Overleaf compiles from the root, so the path becomes `style/resume`.

5. **Set the main document**: **Menu → Main document → examples/resume-en.tex** (or `-fr.tex`). Switch which one is "main" to compile the other language.

### Final layout in Overleaf

```plain
your-project/
├── style/
│   └── resume.sty
└── examples/
    ├── resume-en.tex
    └── resume-fr.tex
```

> **Note:** Overleaf compiles one main document at a time. To produce a merged EN+FR PDF you'd need the local pipeline (`make all`). Overleaf doesn't run the Python merge step.

---

## Adding your content

Once the project compiles, edit the `.tex` file in place. The style provides these commands (defined in `style/resume.sty`):

- `\resumeSubHeadingListStart` / `\resumeSubHeadingListEnd` wrap a list of jobs, projects, or education entries.
- `\resumeSubheading{Title}{Date}{Org}{Location}` is one entry header.
- `\resumeItemListStart` / `\resumeItemListEnd` wrap bullet points under an entry.
- `\resumeItem{...}` is one bullet point.

The dummy resume shows every command in context.

---

## Troubleshooting

### `! LaTeX Error: File 'resume.sty' not found.`

The `.sty` isn't where the `\usepackage` line is looking.

- Layout A: check `resume.sty` is at the project root, not inside a folder.
- Layout B: check the line says `\usepackage{style/resume}` (no `..`) and the file is at `style/resume.sty`.

### `! LaTeX Error: File 'X.sty' not found` (something other than `resume.sty`)

A package required by `style/resume.sty` isn't in Overleaf's TeX Live image. Overleaf ships TeX Live full by default, so this is rare. If it happens, switch the project's TeX Live version under **Menu → Settings → TeX Live version** to the latest.

### Fonts look different from the GitHub Pages preview

Overleaf and the GitHub Action both use TeX Live full, so output should match. If it doesn't, check the **Compiler** setting (Menu → Settings). The template targets `pdfLaTeX`.

### I want CI / auto-publishing

Overleaf doesn't run GitHub Actions. For automated preview, use [Mode 1 (Fork)](../README.md#1-fork-public-cv-repo) or [Mode 2 (Submodule)](../README.md#2-submodule-private-cv-repo). Overleaf alone is editor-only.

---

## Going back to local

If you want PDF merge, QR codes, or CI later, copy your edited `.tex` back into a fork of this repo: drop it in `examples/`, restore the `\usepackage{../style/resume}` line, and run `make all`.

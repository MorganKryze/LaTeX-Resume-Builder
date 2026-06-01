# Migration v1 → v2

A short guide to upgrading a CV that was built with v1.x of this template (style package `style/resume.sty`) to v2.x (document class `style/resume.cls`).

The wire format of every macro you already use is **unchanged** — `\resumeSubheading`, `\resumeItem`, `\resumeItemListStart/End`, etc. all keep their signatures. What changes is how the template is loaded, how the header / education / skills blocks are written, and where you put your overrides.

---

## 1. Switch from package to class

**v1**

```latex
\documentclass[letterpaper,11pt]{article}
\usepackage{../style/resume}
\begin{document}
```

**v2**

```latex
\documentclass[en,11pt]{resume}     % or [fr,11pt], [compact], etc.
\begin{document}
```

Class options:

- `fr` / `en` — language (default `en`; affects babel hyphenation and `\resumeEducationNote` label)
- `compact` / `normal` / `spacious` — spacing density (default `normal`)
- `10pt` / `11pt` / `12pt` — base font size (default `11pt`)

Anything else is forwarded to `article`.

---

## 2. Replace the raw header block with `\resumeHeader` + `\resumeTagline`

**v1**

```latex
\begin{center}
  \textbf{\Huge Jane Doe} \\ \vspace{1pt}
  \href{mailto:jane@example.com}{\underline{jane@example.com}} $|$
  \href{https://linkedin.com/in/jane-doe}{\underline{linkedin.com/in/jane-doe}} $|$
  \href{https://github.com/janedoe}{\underline{github.com/janedoe}} \\
  \vspace{6pt}
  \textbf{\small{Short pitch goes here.}}
\end{center}
```

**v2**

```latex
\resumeHeader{Jane Doe}
  {jane@example.com}
  {linkedin.com/in/jane-doe}
  {github.com/janedoe}
\resumeTagline{Short pitch goes here.}
```

LinkedIn / GitHub args are the displayable form without scheme; the macro prepends `https://` for the link target.

---

## 3. Replace the manual education note with `\resumeEducationNote`

**v1**

```latex
\resumeSubheading{ESILV}{La Défense, Paris}{Cloud \& Cybersécurité}{2021--2026} \\
\vspace{7pt}
\small{\textbf{Projet fin de cursus :} Stocks SSO, dashboard, accès.} \\
\resumeSubheading{Dorset College}{Dublin}{Exchange semester}{2024}
```

**v2**

```latex
\resumeSubheading{ESILV}{La Défense, Paris}{Cloud \& Cybersécurité}{2021--2026}
\resumeEducationNote{Stocks SSO, dashboard, accès.}
\resumeSubheading{Dorset College}{Dublin}{Exchange semester}{2024}
```

The label (`Projet fin de cursus :` / `Capstone project:`) is auto-localised by `\setLanguage`.

---

## 4. Replace the skills `itemize` (or raw `tabular`) with `skillsTable`

**v1 (itemize style)**

```latex
\section{Technical Skills}
\begin{itemize}[leftmargin=0.15in, label={}]
  \small{\item{
    \textbf{Languages :}{ Python, Go} \\
    \textbf{DevOps :}{ Docker, Linux, CI/CD} \\
    ...
  }}
\end{itemize}
```

**v1 (raw tabular variant, also seen in the wild)**

```latex
\section{Compétences}
{\small
\renewcommand{\arraystretch}{1.1}
\noindent
\begin{tabular}{@{\hspace{0.15in}}l@{\hspace{8pt}}p{0.76\textwidth}@{}}
  \textcolor{resumeAccent}{\textbf{Languages}} & Python, Go \\
  \textcolor{resumeAccent}{\textbf{DevOps}}    & Docker, Linux, CI/CD \\
  ...
\end{tabular}
}
```

**v2**

```latex
\section{Compétences}
\begin{skillsTable}
  \skillRow{Languages}{Python, Go}
  \skillRow{DevOps}{Docker, Linux, CI/CD}
  ...
\end{skillsTable}
```

All the layout decisions (fontsize, `arraystretch`, indent, column widths, label colour) now live in the class. The content file carries just the rows.

---

## 5. Migrate configuration from `_accent.tex` → `config.tex`

If you were running the Python pipeline:

- `scripts/write_accent.py` is gone. Run `make config` (or `scripts/write_config.py`) instead. It generates a full `config.tex` next to each resume `.tex`, and removes any leftover `_accent.tex` automatically.
- `options.yml` accepts new optional keys: `font`, `density`, `base_fontsize`, `language`. Setting them in the YAML drives the corresponding `\setBaseFont` / `\setSpacingDensity` / `\setLanguage` calls in the generated `config.tex`. Existing v1 `options.yml` files (with only `accent_color`) keep working — the new keys are optional.

If you were hand-editing `_accent.tex`:

- Move its content into a hand-edited `config.tex` next to your `.tex`. Delete the `% AUTO-GENERATED` header line if you want the Python pipeline to leave your edits alone in the future.

If you were on Overleaf:

- Same as above — replace `_accent.tex` with `config.tex` next to your `.tex` (or at the project root). See [`OVERLEAF.md`](OVERLEAF.md) for the updated walkthrough.

---

## 6. Compile-time path setup

`\documentclass{resume}` looks for `resume.cls` on `TEXINPUTS`, not in a relative path. This template handles it for you in three ways:

- **Local CLI** (`make build`): `scripts/compile_latex.py` sets `TEXINPUTS` automatically.
- **Overleaf**: ship `.latexmkrc` at the project root (already provided). Overleaf reads it before compile.
- **CI**: GitHub Actions step has `env: TEXINPUTS: /github/workspace/style/:` (template) or `/github/workspace/template/style/:` (consumer).

If you compile by hand outside of these flows, run `pdflatex`/`latexmk` with `TEXINPUTS=./style/:` (or `./template/style/:`) prepended.

---

## 7. Verify

```bash
make clean
make build
pdftotext build/resume-en.pdf - | head -50    # sanity-check content
```

Expected: the rendered PDF is visually identical to your v1 build. The `pdftotext` output should preserve all your section names, bullets, and skill rows.

If you see differences in spacing, the new density default (`normal`) may not match your v1 hand-tuned `\vspace` values. Switch to `[compact]` or `[spacious]` on the class options, or fine-tune via `\setSpacingDensity{...}` in `config.tex`.

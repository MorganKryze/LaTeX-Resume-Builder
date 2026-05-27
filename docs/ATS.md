# ATS compatibility

How Applicant Tracking Systems parse PDFs built with this template, what
`style/resume.sty` gets right by default, and the one known limitation you
may want to work around.

## How ATS read PDFs

An ATS is not an AI — it's a text-extraction pipeline:

1. **Glyph → character.** Every PDF stores positioned glyphs. The extractor
   uses each font's _ToUnicode CMap_ to translate glyph IDs back to Unicode.
   Missing or incomplete CMap → garbled text.
2. **Reading order.** Extractors sort text fragments by `y` then `x`.
   Multi-column or right-aligned tabular layouts can be re-grouped as
   separate columns, away from the text they belong to.
3. **Section detection.** Heuristics on header words (`Education`,
   `Experience`, `Skills`, plus localized equivalents) split the document
   into sections.
4. **Keyword matching.** Most ATS run regex/substring matches on the
   extracted text. If `LibreOffice` extracts as `LibreOﬀice` (ff-ligature
   codepoint U+FB00), a search for `office` won't match.
5. **Images and form fields are invisible.** Anything not in the text stream
   is unreachable.

Extractor quality varies. The most basic systems use `pdftotext`. Modern
platforms (Workday, Greenhouse, Lever, SmartRecruiters) use Apache PDFBox,
pdf.js, or proprietary parsers — significantly better at reading order and
column detection.

## What `resume.sty` gets right (built in)

- **T1 + Latin Modern fonts.** `\RequirePackage[T1]{fontenc}` and
  `\RequirePackage{lmodern}` are loaded by default. Latin Modern is a
  Unicode-aware drop-in replacement for Computer Modern: same visual at
  body-text size, but every glyph (including the `ff`/`fi`/`fl`/`ffi`/`ffl`
  ligatures) carries a proper ToUnicode mapping. Words like `LibreOffice`
  extract as plain ASCII, not as Unicode ligature codepoints.
- **ToUnicode tables generated.** `\pdfgentounicode=1` plus
  `\input{glyphtounicode}` (both inside an `\ifPDFTeX` guard) cover
  accented characters and most special glyphs.
- **No headers, footers, page numbers, watermarks, or background images**
  in the body. `\fancyhf{}` clears everything; nothing leaks into the
  extracted text.
- **Real bullets via `itemize`.** Each `\resumeItem` is a true list item,
  so bullets extract as the U+2022 character attached to their text.
- **Standard section names.** Authors typically use `Education`,
  `Experience`, `Projects`, `Skills` (or `Formation`, `Expériences`,
  `Projets`, `Compétences`) — all recognized by mainstream ATS
  dictionaries.
- **Real hyperlinks.** `\href{URL}{visible text}` puts the URL in the
  annotation layer and the visible text in the content stream. Authors
  should put identifying text (`linkedin.com/in/…`, `github.com/…`) in the
  visible portion so ATS that ignore annotations still see it.
- **Single-column body, no math, no data tables.** The body flows linearly.

## Configuring the accent color

The accent color is **a single field** in `options.yml`, shared across the
resume PDF (section rules + hyperlinks), the QR code, and the gh-pages
download button.

```yaml
# options.yml
accent_color: [15, 55, 120] # RGB triple; navy by default
```

At build time `scripts/write_accent.py` reads this value and writes a
one-line `_accent.tex` next to each declared resume source:

```latex
\definecolor{resumeAccent}{RGB}{15,55,120}
```

`style/resume.sty` does `\IfFileExists{_accent.tex}{\input{_accent.tex}}{}`
after defaulting `resumeAccent` to black, so the generated file wins when
present. Skipping the `accent_color` field falls back to the default black
(visually identical to pre-accent releases).

The same `accent_color` value is read by `scripts/generate_qr_code.py` for
the QR eye color and by the CI's gh-pages assembly step for the download
button (a `--accent-hover` shade is derived by darkening, and a
contrast-safe text color is picked via relative luminance).

You can still override directly in your content's preamble if you want a
different accent for the PDF only — `\definecolor{resumeAccent}{HTML}{…}`
or `\colorlet{resumeAccent}{NavyBlue}` after the `\usepackage` line. The
content-level override wins because it loads after `_accent.tex`.

Nothing else changes — section text, body, bullets, and bold company names
stay black. ATS extraction is unaffected by colored rules and links (color
is a graphic property; the underlying text is untouched).

## Known limitation: right-aligned dates in two-column subheadings

`\resumeSubheading` and `\resumeProjectHeading` use a `tabular*` with
`\extracolsep{\fill}` to put dates and locations in a right-aligned column.
In sections with bullets _between_ entries (typical for Experience and
Projects), basic extractors stay in source order — the bullets break their
column-detection heuristic.

In sections where two `\resumeSubheading` entries sit back-to-back **with
no bullets between them** (e.g. an Education section with two schools,
neither using `\resumeItem`s), basic `pdftotext`-style extractors detect
the right side as a separate column and group it at the bottom:

```plain
School A
Degree A description

School B
Degree B description

City A           ← detached from School A
Date range A
City B           ← detached from School B
Date range B
```

The data is all present — just not paired up in basic extraction.

**Impact in practice.** Modern ATS handle right-aligned date columns
correctly. This only affects systems that fall back to `pdftotext`-grade
extraction (older in-house ATS, simple resume-parser SaaS, manual
copy-paste).

**Workarounds.**

- **Add at least one bullet to each entry.** A `\resumeItem` between
  back-to-back subheadings is usually enough to break the column-detection
  heuristic.
- **Inline the dates** by redefining the heading macros in your own
  override `.sty`:

  ```latex
  \renewcommand{\resumeSubheading}[4]{
    \vspace{-2pt}\item
      \textbf{#1} \textemdash{} #2\\
      \textit{\small#3} \textemdash{} \textit{\small#4}
      \vspace{-7pt}
  }
  ```

  Reliable across every parser; sacrifices the right-aligned date column
  aesthetic.

## How to verify what an ATS sees

After building, dump the extracted text:

```bash
pdftotext build/resume-<lang>.pdf -          # raw, content-stream order
pdftotext -layout build/resume-<lang>.pdf -  # spatial layout preserved
```

Things to check in the output:

- Every section header on its own line
- Bullets (`•`) immediately followed by the bullet text
- No Unicode ligature codepoints (`ﬀ`, `ﬁ`, `ﬂ`); detect with
  `pdftotext build/resume-<lang>.pdf - | grep -P '[\x{FB00}-\x{FB04}]'`
- Accented characters preserved (`é`, `à`, `ç`)
- Skills section reads as `Category : item, item, item`

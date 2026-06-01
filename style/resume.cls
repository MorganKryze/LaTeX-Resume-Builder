%---------------------------------------------------------------
% resume.cls — LaTeX document class for the Resume-LaTeX template
% Maintainer: Yann M. Vidamment
% License: MIT (see LICENSE, with attribution to sb2nov & jakegut)
% Based on:
%   https://github.com/jakegut/resume
%   https://github.com/sb2nov/resume
%---------------------------------------------------------------
% Usage:
%   \documentclass[fr,11pt,normal]{resume}
%
% Class options:
%   Language  : fr | en                       (default: en)
%   Density   : compact | normal | spacious   (default: normal)
%   Font size : 10pt | 11pt | 12pt            (default: 11pt)
%
% Optional user configuration (workspace-side):
%   config.tex next to the .tex source — \definecolor{resumeAccent},
%   \setSpacingDensity, \setBaseFont, \setLanguage. See config.example.tex.
%
% Public macros: see commands section at the bottom of this file.
%---------------------------------------------------------------

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{resume}[2026/06/01 v2.0.0 Resume class]

%------------ETOOLBOX (needed for toggles/conditionals)-------
\RequirePackage{etoolbox}

%------------DEFAULTS + TOGGLES-----------
\newtoggle{resume@compact}
\newtoggle{resume@spacious}
\newcommand{\resume@font}{sourcesans}     % sourcesans | firasans | latinmodern
\newcommand{\resume@lang}{en}             % en | fr
\newcommand{\resume@fontsize}{11pt}

%------------CLASS OPTIONS----------------
\DeclareOption{fr}{\renewcommand{\resume@lang}{fr}}
\DeclareOption{en}{\renewcommand{\resume@lang}{en}}
\DeclareOption{compact}{\toggletrue{resume@compact}}
\DeclareOption{normal}{}
\DeclareOption{spacious}{\toggletrue{resume@spacious}}
\DeclareOption{10pt}{\renewcommand{\resume@fontsize}{10pt}}
\DeclareOption{11pt}{\renewcommand{\resume@fontsize}{11pt}}
\DeclareOption{12pt}{\renewcommand{\resume@fontsize}{12pt}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass[\resume@fontsize,letterpaper]{article}

%------------DENSITY-AWARE LENGTHS--------
% Three internal lengths drive every vertical adjustment in macros below,
% replacing the hardcoded -2pt / -5pt / -7pt sprinkled in v1's resume.sty.
\newlength{\resume@vTight}     % small tight pull (legacy -2pt)
\newlength{\resume@vGap}       % bullet/list end pull (legacy -5pt)
\newlength{\resume@vSection}   % subheading bottom pull (legacy -7pt)

\newcommand{\resume@applyDensity}{%
  \iftoggle{resume@compact}{%
    \setlength{\resume@vTight}{-3pt}%
    \setlength{\resume@vGap}{-4pt}%
    \setlength{\resume@vSection}{-4pt}%
  }{\iftoggle{resume@spacious}{%
    \setlength{\resume@vTight}{0pt}%
    \setlength{\resume@vGap}{4pt}%
    \setlength{\resume@vSection}{4pt}%
  }{% normal
    \setlength{\resume@vTight}{-2pt}%
    \setlength{\resume@vGap}{1pt}%
    \setlength{\resume@vSection}{1pt}%
  }}%
}
\resume@applyDensity

%------------PUBLIC SETTERS---------------
% Callable from config.tex. They mutate toggles/state and re-apply where needed.
\newcommand{\setSpacingDensity}[1]{%
  \togglefalse{resume@compact}\togglefalse{resume@spacious}%
  \ifstrequal{#1}{compact}{\toggletrue{resume@compact}}{}%
  \ifstrequal{#1}{spacious}{\toggletrue{resume@spacious}}{}%
  \resume@applyDensity%
}
\newcommand{\setBaseFont}[1]{\renewcommand{\resume@font}{#1}}
\newcommand{\setLanguage}[1]{\renewcommand{\resume@lang}{#1}}

%------------DEFAULT ACCENT---------------
\RequirePackage[dvipsnames]{xcolor}
\definecolor{resumeAccent}{HTML}{000000}

%------------USER CONFIG (optional)-------
% Loaded next to the compiled .tex (same cwd). Use it to override accent
% color, density, font, language. Hand-editable; the Python pipeline
% (scripts/write_config.py) can regenerate it from options.yml.
\InputIfFileExists{config.tex}{}{}

%------------CORE PACKAGES----------------
\RequirePackage{latexsym}
% T1 + Latin Modern for math + ATS-friendly Unicode CMap, regardless of
% the chosen body font (lmodern serves the math; body is swapped below).
\RequirePackage[T1]{fontenc}
\RequirePackage{lmodern}

%------------BODY FONT (conditional)------
\ifdefstring{\resume@font}{firasans}{%
  \RequirePackage[sfdefault,scaled=0.95]{FiraSans}%
}{\ifdefstring{\resume@font}{latinmodern}{%
  % lmodern is already loaded above and acts as the body font.
}{%
  \RequirePackage[default]{sourcesanspro}%
}}

\RequirePackage[empty]{fullpage}
\RequirePackage{titlesec}
\RequirePackage{marvosym}
\RequirePackage{verbatim}
\RequirePackage{enumitem}
\RequirePackage{hyperref}
\RequirePackage{bookmark}
\RequirePackage{fancyhdr}

%------------BABEL (conditional)----------
\ifdefstring{\resume@lang}{fr}{%
  \RequirePackage[french]{babel}%
}{%
  \RequirePackage[english]{babel}%
}

\RequirePackage{tabularx}
\RequirePackage{iftex}
% pdfTeX-only ATS Unicode mappings; XeTeX/LuaTeX do not define these primitives.
\ifPDFTeX
\input{glyphtounicode}
\fi

%------------HYPERREF SETUP---------------
\hypersetup{
  colorlinks=true,
  urlcolor=resumeAccent,
  linkcolor=resumeAccent,
  citecolor=resumeAccent,
  pdfborder={0 0 0}
}

%------------FORMATTING-------------------
\setlength{\footskip}{5pt}
\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

%------------MARGINS----------------------
\addtolength{\oddsidemargin}{-0.65in}
\addtolength{\evensidemargin}{-0.65in}
\addtolength{\textwidth}{1.3in}
\addtolength{\topmargin}{-.8in}
\addtolength{\textheight}{1.5in}

%------------GENERAL----------------------
\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Inline emphasis for key numbers/keywords in body text.
% Source Sans 3 doesn't expose a separate semibold series in TU encoding,
% so we use \textbf (= the bold weight of Source Sans, which is itself
% a "thin bold" relative to Latin Modern's heavier bx). Sparing use only.
\newcommand{\hl}[1]{\textbf{#1}}

% Section title + horizontal rule on the SAME line (rule fills to right margin).
\newcommand{\sectionrule}[1]{#1\hspace{0.5em}{\color{resumeAccent}\hrulefill}}
\titleformat{\section}{%
  \vspace{-6pt}\raggedright\Large\bfseries
}{}{0em}{\sectionrule}[\vspace{-8pt}]

% Ensure generated pdf is machine readable / ATS parsable
\ifPDFTeX
\pdfgentounicode=1
\fi

%------------PUBLIC MACROS (existing)-----
\newcommand{\resumeItem}[1]{%
  \item\small{%
    {#1 \vspace{\resume@vTight}}%
  }%
}

\newcommand{\resumeSubheading}[4]{%
  \vspace{\resume@vTight}\item%
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{\resume@vSection}%
}

\newcommand{\resumeSubSubheading}[2]{%
    \item%
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{\resume@vSection}%
}

\newcommand{\resumeProjectHeading}[2]{%
    \vspace{2pt}\item%
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      #1 & #2 \\
    \end{tabular*}\vspace{\resume@vGap}%
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

% Bullet for level-2 itemize items (the actual resume bullets).
% Wrapped in \AtBeginDocument so babel-french (which redefines \labelitemii
% to an en-dash via its own \AtBeginDocument hook) doesn't overwrite us.
\AtBeginDocument{%
  \renewcommand\labelitemii{{\color{resumeAccent}$\vcenter{\hbox{\tiny$\bullet$}}$}}%
}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{\resume@vGap}}

%------------PUBLIC MACROS (new in v2)----

% \resumeHeader{name}{email}{linkedin-host-and-path}{github-host-and-path}
% Centred header block: huge name + three underlined hyperlinks separated by |.
% LinkedIn/GitHub args are the displayable form without scheme (e.g.,
% "linkedin.com/in/jdoe"); the macro prepends https:// for the URL.
\newcommand{\resumeHeader}[4]{%
  \begin{center}
    \textbf{\Huge #1} \\ \vspace{1pt}
    \href{mailto:#2}{\underline{#2}} $|$
    \href{https://#3}{\underline{#3}} $|$
    \href{https://#4}{\underline{#4}} \\
  \end{center}%
}

% \resumeTagline{text}
% Bold small-font paragraph that sits directly under the header. Used for
% the short pitch (role, current focus, target opportunity).
\newcommand{\resumeTagline}[1]{\textbf{\small{#1}}}

% \resumeEducationNote{text}
% Education annotation rendered between \resumeSubheading calls inside a
% \resumeSubHeadingListStart...End block. Auto-localised label. Renders in
% \footnotesize (one step smaller than the description above it) and sits
% close to its parent subheading, with breathing space below before the
% next subheading.
\newcommand{\resumeEducationNote}[1]{%
  \\%
  {\fontsize{9.5pt}{11pt}\selectfont\textbf{%
    \ifdefstring{\resume@lang}{fr}{Projet fin de cursus :}{Capstone project:}%
  }\ #1}%
  \\ \vspace{6pt}%
}

% skillsTable environment + \skillRow{label}{content}
% Two-column table for the "Compétences/Skills" section. Labels in accent
% colour and bold (left, narrow column, auto-sized to widest label),
% content in default style (right, ~0.76\textwidth wide, wraps if needed).
\newenvironment{skillsTable}
  {\par\small\renewcommand{\arraystretch}{1.1}%
   \noindent\tabular{@{\hspace{0.15in}}l@{\hspace{8pt}}p{0.76\textwidth}@{}}}
  {\endtabular\par}
\newcommand{\skillRow}[2]{\textcolor{resumeAccent}{\textbf{#1}} & #2 \\}

\endinput

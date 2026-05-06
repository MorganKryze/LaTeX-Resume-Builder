# Contributing

Thanks for considering a contribution. This project favors small, focused PRs that respect the style/content boundary at the core of the architecture.

## Core principle

**The template must never impose content.** A change that adds a required section, a required field in `options.yml`, or a hardcoded string only relevant to one person's CV is out of scope.

## Local setup

```bash
git clone https://github.com/MorganKryze/LaTeX-Resume-Builder.git
cd LaTeX-Resume-Builder
make install
make test lint
make all                 # sanity build of the Jane Doe dummy
```

## LaTeX conventions

- New commands go in `style/resume.sty`. Follow the existing naming (`\resume<Thing>`).
- Keep the package self-contained: any added `\RequirePackage` must be listed in `style/resume.sty` and documented in `docs/USAGE.md` troubleshooting if it's unusual.
- No content in the `.sty`. No `\newcommand{\myName}{...}`.

## Python conventions

- Dependency manager: [`uv`](https://docs.astral.sh/uv/). Runtime deps in `[project.dependencies]` in `pyproject.toml`, dev deps in `[dependency-groups].dev`. The `uv.lock` file is committed; do not remove it.
- Formatter: `black --line-length 100`. Linter: `ruff` with the rules in `pyproject.toml`.
- All scripts in `scripts/` are CLIs parameterized by `--config` and `--project-root`. Do not hardcode paths.
- New CLI → new tests in `tests/tests.py`. Don't add functionality that has no test.

## Running checks locally (what CI runs)

```bash
make lint        # ruff + black --check
make test        # unittest
```

If either fails, CI will fail. Run them before pushing.

## PR checklist

- [ ] `make lint` passes
- [ ] `make test` passes
- [ ] `make all` produces a valid `build/resume.pdf` from the Jane Doe dummy
- [ ] New or changed YAML keys documented in `docs/USAGE.md`
- [ ] New behavior covered by a test
- [ ] No personal content leaked into `examples/`

`CHANGELOG.md` is **not** edited in feature PRs. It is updated only when cutting
a new version (see [Releases](#releases) below).

## Commit message style

Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `ci:`, `refactor:`, `test:`. Scope is optional.

Examples:

```plain
feat(scripts): allow http(s) URL for image_source
fix(ci): correct poppler install on ubuntu-24.04
docs: clarify submodule PROJECT_ROOT semantics
```

## Releases

`CHANGELOG.md` is regenerated only when cutting a new version. The release
flow:

1. Decide the version bump (semver: patch / minor / major).
2. Read the commit history since the last tag:
   ```bash
   git log v1.0.0..HEAD --pretty=format:'%h %s'
   ```
3. Group those commits under the Keep a Changelog headings (`Security`,
   `Fixed`, `Added`, `Changed`, `Removed`, `Deprecated`). Conventional Commit
   prefixes (`feat`, `fix`, `docs`, `chore`, `ci`, `refactor`, `test`) make this
   straightforward.
4. Write the entry above the previous version in `CHANGELOG.md`, with the date
   in `YYYY-MM-DD` and a one-paragraph release summary at the top.
5. Commit the `CHANGELOG.md` update on its own (`docs: changelog for vX.Y.Z`).
6. Tag and push:
   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin main vX.Y.Z
   ```

Between releases, `git log` is the source of truth for what changed. Feature
PRs do not touch `CHANGELOG.md`.

## Scope of changes

Welcome:

- Bug fixes
- New `--flag` options that stay backward-compatible
- Docs improvements
- New languages in `examples/` (stay with the Jane Doe persona)
- Packaging or CI hardening

Out of scope:

- Rewrites that change the YAML schema without a migration path
- Additions that embed a specific person's content
- Heavy new dependencies without clear justification

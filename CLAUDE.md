# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

MkDocs template for publishing documentation to the Knowledge Base. Python-based, no Node.js required. Custom Jinja2 theme with pre-built Tailwind CSS in `theme/`.

## Build Commands

```bash
npm run preview        # build + serve dist/ at :8000 (full site with showcase)
npm run dev            # mkdocs serve with live reload (docs only, no showcase)
npm run build          # standalone build
npm run build:headless # headless build (no top nav, for knowledge base embedding)
```

`run.js` auto-detects `python3` or `python` — works on Windows and Linux/Mac.

Direct invocation (skipping npm):
```bash
python scripts/pack.py
python scripts/pack.py --headless
```

Output: `dist.tar.gz` containing `dist/` + `marketplace.json`.

Set `SKIP_PIP_INSTALL=1` to skip automatic pip install in managed environments.

## Build Pipeline (scripts/pack.py)

1. Install deps from `requirements.txt` (just MkDocs 1.6.1)
2. Merge `mkdocs.yml` + any wiki pages from `docs/wiki/` into temporary `mkdocs-build.yml`
3. Run `mkdocs build` against merged config
4. Copy `showcase.html` as `dist/index.html` entry point (headless strips `<nav>`)
5. Generate `dist/marketplace.json` with pages manifest derived from nav config
6. Package into `dist.tar.gz`

Temporary build configs (`mkdocs-build.yml`, `mkdocs-headless-build.yml`) are cleaned up on exit.

## Architecture

```
docs/              → Markdown source files with YAML frontmatter
theme/main.html    → Jinja2 page template (branded, dark mode toggle)
theme/style.css    → Pre-compiled Tailwind CSS (edit Tailwind source to regenerate)
scripts/pack.py    → Primary build script (cross-platform Python)
scripts/pack.sh    → Bash build script (Linux/CI alternative)
run.js             → Node wrapper: auto-detects python, invokes pack.py
showcase.html      → Product landing page, becomes dist/index.html
marketplace.json   → Knowledge base manifest (name, slug, icon, tags)
mkdocs.yml         → MkDocs config: nav structure, theme, docs/site dirs
```

## Documentation Conventions

Frontmatter format for pages in `docs/`:
```yaml
---
title: Page Title
order: 1
section: Optional Section Name
---
```

- Navigation order is defined in `mkdocs.yml` `nav:` section
- `order` and `section` in frontmatter feed into `dist/marketplace.json` pages manifest
- Wiki pages placed in `docs/wiki/` are auto-discovered and appended as a "Wiki" nav section

## MkDocs Theme

- `theme.name` is `null` — uses fully custom theme from `theme/` directory
- `theme/main.html` uses Jinja2 with MkDocs template variables (`page.title`, `page.content`, `config.site_name`)
- Headless mode detected via `config.extra.headless` — hides logo and navigation

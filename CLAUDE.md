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

1. Install deps from `requirements.txt` (MkDocs 1.6.1 + Jinja2)
2. Auto-generate nav from `docs/` frontmatter (title, order, section) + wiki pages
3. Write merged config to temporary `mkdocs-build.yml`
4. Run `mkdocs build` against merged config
5. Render `showcase.html` template with `data/showcase.yml` → `dist/index.html` (headless strips `<nav>`)
6. Copy `showcase.css` → `dist/showcase.css`
7. Generate `dist/marketplace.json` with pages manifest
8. Package into `dist.tar.gz`

`pack.py --serve` generates config then runs `mkdocs serve` with auto-nav (used by `npm run dev`).

Temporary build configs (`mkdocs-build.yml`, `mkdocs-headless-build.yml`) are cleaned up on exit.

## Architecture

```
docs/              → Markdown source files with YAML frontmatter
data/showcase.yml  → Showcase landing page content (CMS-editable)
theme/main.html    → Jinja2 page template (branded, dark mode toggle)
theme/style.css    → Pre-compiled Tailwind CSS (edit Tailwind source to regenerate)
showcase.html      → Jinja2 template for showcase (rendered from data/showcase.yml)
showcase.css       → Showcase page styles (copied to dist/ at build time)
scripts/pack.py    → Primary build script (cross-platform Python)
scripts/pack.sh    → Bash build script (Linux/CI alternative)
run.js             → Node wrapper: auto-detects python, invokes pack.py
marketplace.json   → Knowledge base manifest (name, slug, icon, tags)
mkdocs.yml         → MkDocs config: theme, docs/site dirs (nav is auto-generated)
admin/index.html   → Sveltia CMS entry point
admin/config.yml   → Sveltia CMS collections and backend config
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

- Navigation is **auto-generated** from frontmatter at build time — no manual `nav:` editing
- Pages are sorted by `order`; pages with `section` are grouped under that section heading
- Wiki pages placed in `docs/wiki/` are auto-discovered and appended as a "Wiki" nav section
- `order` and `section` in frontmatter also feed into `dist/marketplace.json` pages manifest

## CMS (Sveltia CMS)

- Admin panel at `/admin/` — loads Sveltia CMS from CDN
- Backend: GitHub (configure `backend.repo` in `admin/config.yml`)
- Collections: docs (folder), showcase (file), marketplace metadata (file)
- Showcase content lives in `data/showcase.yml` — rendered via Jinja2 template at build time
- CMS commits trigger CI build; no separate build step needed

## MkDocs Theme

- `theme.name` is `null` — uses fully custom theme from `theme/` directory
- `theme/main.html` uses Jinja2 with MkDocs template variables (`page.title`, `page.content`, `config.site_name`)
- Headless mode detected via `config.extra.headless` — hides logo and navigation

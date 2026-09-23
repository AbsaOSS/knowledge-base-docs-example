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

Builds write to `dist/`. Nothing is packaged by default — the release workflow hands `dist/` + `kb-docs.json` to the reusable `AbsaOSS/knowledge-base/actions/publish-docs` action, which validates, packs `kb-docs.tar.gz` and attaches it to the GitHub Release.

`run.js` auto-detects `python3` or `python` — works on Windows and Linux/Mac.

Direct invocation (skipping npm):
```bash
python scripts/pack.py
python scripts/pack.py --headless
python scripts/pack.py --pack      # headless + local kb-docs.tar.gz (same layout as the action)
```

`--pack` output: `kb-docs.tar.gz` containing `kb-docs.json` + `user-guide/` (the built `dist/`, named after the slug). Local inspection only; CI never runs it.

Set `SKIP_PIP_INSTALL=1` to skip automatic pip install in managed environments.

## Build Pipeline (scripts/pack.py)

1. Install deps from `requirements.txt` (MkDocs 1.6.1 + Jinja2)
2. Auto-generate nav from `docs/` frontmatter (title, order, section) + wiki pages
3. Write merged config to temporary `mkdocs-build.yml`
4. Run `mkdocs build` against merged config
5. Wrap the raw HTML under `content:` in `data/showcase.yml` into `dist/index.html` (headless strips the `<nav>` between the Navigation markers and adds `data-kb-headless="true"`)
6. Copy `showcase.css` → `dist/showcase.css` (`admin/` too, standalone only)
7. Write the computed `pages` list into `apps[0].pages` of `kb-docs.json` (in place; only that key is touched)
8. `--pack` only: verify headless rules and pack `kb-docs.tar.gz`

`pack.py --serve` generates config then runs `mkdocs serve` with auto-nav (used by `npm run dev`).

Temporary build configs (`mkdocs-build.yml`, `mkdocs-headless-build.yml`) are cleaned up on exit.

## Architecture

```
docs/              → Markdown source files with YAML frontmatter
data/showcase.yml  → Showcase landing page content (CMS-editable)
theme/main.html    → Jinja2 page template (branded, dark mode toggle)
theme/style.css    → Pre-compiled Tailwind CSS (edit Tailwind source to regenerate)
showcase.html      → legacy Jinja2 showcase template; NOT used by the build (content lives in data/showcase.yml)
showcase.css       → Showcase page styles (copied to dist/ at build time)
scripts/pack.py    → Primary build script (cross-platform Python)
scripts/pack.sh    → Bash build script (Linux/CI alternative)
run.js             → Node wrapper: auto-detects python, invokes pack.py
kb-docs.json       → Knowledge base manifest, contract v1 (kbVersion, apps[0]: slug, name, icon, tags, pages)
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
- `order` and `section` in frontmatter also feed into the `pages` manifest written into `kb-docs.json`

## CMS (Sveltia CMS)

- Admin panel at `/admin/` — loads Sveltia CMS from CDN
- Backend: GitHub (configure `backend.repo` in `admin/config.yml`)
- Collections: docs (folder), showcase (file), knowledge base metadata `kb-docs.json` (file)
- Showcase content lives in `data/showcase.yml` as raw HTML (`content:` key) — wrapped into a full page at build time
- CMS commits trigger CI build; no separate build step needed

## MkDocs Theme

- `theme.name` is `null` — uses fully custom theme from `theme/` directory
- `theme/main.html` uses Jinja2 with MkDocs template variables (`page.title`, `page.content`, `config.site_name`)
- Headless mode detected via `config.extra.headless` — hides logo, navigation, theme toggle and dark-mode bootstrap; sets `data-kb-headless="true"` on `<html>` (the knowledge base verifies this on every page)

## Knowledge Base Contract

- Normative spec: `contract/ARTIFACT.md`, `contract/HEADLESS_RULES.md`, `contract/kb-docs.schema.json` in AbsaOSS/knowledge-base
- Publishing: `.github/workflows/pack.yml` runs on `release: published` (checkout → setup-python → `pack.py --headless` → `actions/publish-docs@v1`). Keep it minimal — this repo is the template other docs repos copy
- PR check: `.github/workflows/check-docs.yml` runs on `pull_request` with the same build, then `actions/check-docs@v1` (same contract checks, no release; errors fail, warnings annotated, `strict` off). Preview locally: `node ../knowledge-base/actions/lib/check-cli.js --manifest kb-docs.json --dist dist`
- Registry entry in the knowledge base is just `{ "repo": "AbsaOSS/knowledge-base-docs-example", "version": "latest" }`; all display metadata lives in `kb-docs.json` here

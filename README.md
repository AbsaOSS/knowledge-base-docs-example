# Knowledge Base — User Guide Template

A full user guide and template for building documentation sites that integrate with the
Knowledge Base.
Built with [MkDocs](https://www.mkdocs.org/) — no Node.js required.

## What's included

| File / Folder | Purpose |
|---|---|
| `docs/*.md` | Markdown source pages (user guide content) |
| `docs/showcase/` | Three interlinked showcase pages demonstrating content patterns |
| `mkdocs.yml` | Site configuration — nav order, site name |
| `mkdocs-headless.yml` | Headless build config (inherits from `mkdocs.yml`) |
| `theme/main.html` | Jinja2 page template with nav + dark mode |
| `theme/style.css` | Pre-built branded Tailwind CSS (no compilation needed) |
| `marketplace.json` | Knowledge base manifest |
| `scripts/` | Build + package scripts (`pack.py`, `pack.sh`) |
| `.github/workflows/release.yml` | Auto-publish on `v*` tags |

## Quick start

```bash
pip install -r requirements.txt   # install MkDocs (once)
mkdocs serve                      # live-reload at http://localhost:8000
```

Or via npm (installs and runs in one step):

```bash
npm run preview
```

## Build

```bash
npm run build           # standalone (with top nav + theme toggle)
npm run build:headless  # headless (knowledge-base-ready, no top nav)
```

## Adding a page

1. Create `docs/my-page.md` with a title in frontmatter:

```markdown
---
title: My Page
---
# My Page
Content here.
```

2. Add it to `nav:` in `mkdocs.yml`:

```yaml
nav:
  - Overview: index.md
  - My Page: my-page.md
```

That is all — no changes to build scripts or CSS are needed.

## Publishing a release

```bash
git tag v1.0.0 && git push origin v1.0.0
```

The release workflow builds the headless site, packages `dist/` + `marketplace.json`
into `dist.tar.gz`, and creates a GitHub Release. The knowledge base fetches this artifact automatically.

## Registering in the knowledge base

Add an entry to `apps.json` in the knowledge base repo:

```json
{
  "repo": "your-org/your-docs-repo",
  "slug": "user-guide",
  "name": "Knowledge Base User Guide",
  "description": "Everything you need to publish your own docs.",
  "icon": "book-open",
  "tags": ["guide"],
  "version": "latest"
}
```

See `HEADLESS_RULES.md` in the knowledge base repo for the full integration contract.


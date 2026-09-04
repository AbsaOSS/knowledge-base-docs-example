---
title: Overview
order: 1
---

# Knowledge Base Docs Example

A ready-to-use MkDocs template for publishing documentation to the Knowledge Base. Clone it, write Markdown, tag a release — your docs are live.

## What is included

| File / Folder | Purpose |
|---|---|
| `docs/*.md` | Your Markdown content — edit these |
| `mkdocs.yml` | Site config — update `site_name` (nav is auto-generated) |
| `data/showcase.yml` | Product landing page content — edit to match your tool |
| `kb-docs.json` | Knowledge base manifest — set your `slug`, `name`, `description` |
| `theme/` | Pre-built branded theme — no changes needed |
| `requirements.txt` | Python dependencies — no changes needed |
| `scripts/` | Build + package scripts — no changes needed |
| `.github/workflows/pack.yml` | Publishes to the knowledge base on release — no changes needed |

## Quick start

```bash
# 1 — clone
git clone <your-repo-url> my-team-docs
cd my-team-docs

# 2 — install MkDocs (one time)
pip install -r requirements.txt

# 3 — live preview at http://localhost:8000
mkdocs serve
```

## What you need to change

Only three things need updating to make this template your own:

1. **`kb-docs.json`** — set your `slug`, `name`, and `description`
2. **`mkdocs.yml`** — set `site_name`
3. **`docs/*.md`** — replace the starter pages with your content

The build script, CSS, and CI pipeline work out of the box and never need to be touched.

## Full documentation

The complete user guide — including tool setup for non-technical writers and the knowledge base registration process — is available in the knowledge base documentation.

Continue reading: [Customising](customising.md) · [Adding Pages](adding-pages.md)

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
| `mkdocs.yml` | Site config — update `site_name` and `nav:` |
| `showcase.html` | Product landing page — edit to match your tool |
| `theme/` | Pre-built branded theme — no changes needed |
| `requirements.txt` | Python dependencies — no changes needed |
| `scripts/` | Build + package scripts — no changes needed |
| `.github/workflows/release.yml` | CI/CD pipeline — no changes needed |

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

1. **`marketplace.json`** — set your `slug`, `name`, and `description`
2. **`mkdocs.yml`** — set `site_name` and update the `nav:` entries
3. **`docs/*.md`** — replace the starter pages with your content

The build script, CSS, and CI pipeline work out of the box and never need to be touched.

## Full documentation

The complete user guide — including tool setup for non-technical writers and the knowledge base registration process — is available in the knowledge base documentation.

Continue reading: [Customising](customising.md) · [Adding Pages](adding-pages.md)

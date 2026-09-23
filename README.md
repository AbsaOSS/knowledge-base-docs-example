# Knowledge Base — User Guide Template

A full user guide and template for building documentation sites that integrate with the
Knowledge Base.
Built with [MkDocs](https://www.mkdocs.org/) — no Node.js required.

## What's included

| File / Folder | Purpose |
|---|---|
| `docs/*.md` | Markdown source pages (user guide content) |
| `data/showcase.yml` | Showcase landing page content (CMS-editable) |
| `mkdocs.yml` | Site configuration — site name (nav is auto-generated) |
| `theme/main.html` | Jinja2 page template with nav + dark mode |
| `theme/style.css` | Pre-built branded Tailwind CSS (no compilation needed) |
| `kb-docs.json` | Knowledge base manifest (contract v1) |
| `scripts/` | Build scripts (`pack.py`, `pack.sh`) |
| `.github/workflows/pack.yml` | Publishes `kb-docs.tar.gz` to the knowledge base on every GitHub Release |
| `.github/workflows/check-docs.yml` | Runs the same contract checks on every pull request |

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

To inspect exactly what the knowledge base will receive, pack the headless build
locally the same way the publish action does:

```bash
python scripts/pack.py --pack     # → kb-docs.tar.gz (kb-docs.json + user-guide/)
```

## Adding a page

Create `docs/my-page.md` with a title and order in frontmatter:

```markdown
---
title: My Page
order: 4
---
# My Page
Content here.
```

That is all — navigation and the `pages` list in `kb-docs.json` are generated from
frontmatter at build time. No changes to `mkdocs.yml`, build scripts or CSS are needed.

## Publishing a release

Publish a GitHub Release — the tag is created for you if it does not exist:

```bash
gh release create v2.0.0 --generate-notes
```

The `Publish docs` workflow builds the headless site and hands `dist/` + `kb-docs.json`
to `AbsaOSS/knowledge-base/actions/publish-docs`, which validates them against the
contract, packs `kb-docs.tar.gz` and attaches it to the release. The knowledge base
fetches this artifact automatically.

The `Check docs` workflow runs the same checks on every pull request
(`AbsaOSS/knowledge-base/actions/check-docs`), without releasing anything. Errors fail
the pull request; warnings are annotated and listed in the job summary.

## Registering in the knowledge base

Add a two-line entry to `apps.json` in the knowledge base repo:

```json
{ "repo": "your-org/your-docs-repo", "version": "latest" }
```

Name, description, icon, tags, slug and pages are all read from your `kb-docs.json`, so
changing them later never touches the knowledge base repository.

See `contract/ARTIFACT.md` and `contract/HEADLESS_RULES.md` in the knowledge base repo for
the full integration contract.

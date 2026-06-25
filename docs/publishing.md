---
title: Publishing to the Knowledge Base
order: 5
---

# Publishing to the Knowledge Base

This page explains how a docs app is **packed** into a release artifact and how the
Knowledge Base picks it up and serves it under a shared URL.

You author Markdown; the build script produces a self-contained static site plus a
manifest. The Knowledge Base downloads that artifact, rewrites its links, wraps it in
shared chrome, and serves it at `/{prefix}/{slug}/`.

## The packaging artifact

The build produces a single file: **`dist.tar.gz`**. It contains the rendered site and
the manifest the Knowledge Base reads to register your app.

```
dist.tar.gz
├── dist/
│   ├── index.html          ← showcase landing (entry point)
│   ├── docs/
│   │   ├── index.html       ← rendered Markdown pages
│   │   └── <page>/index.html
│   ├── style.css
│   ├── showcase.css
│   └── marketplace.json     ← optional, overrides root manifest with computed pages
└── marketplace.json         ← root manifest (name, slug, pages, …)
```

Build it locally:

```bash
python scripts/pack.py --headless     # or: bash scripts/pack.sh --headless
```

Output lands at the repo root as `dist.tar.gz`. See the [build pipeline](#build-pipeline)
below for what each step does.

## Headless builds

The Knowledge Base embeds your pages **inside its own chrome** (top bar, theme toggle,
unified navigation). To avoid a doubled header and broken layout, apps publish a
**headless** build.

Headless mode (`--headless`) changes the output so it embeds cleanly:

- The site `<header>` (logo + top nav) is omitted — the Knowledge Base supplies the top bar.
- `data-mp-headless="true"` is set on `<html>` so the Knowledge Base can verify the page is headless.
- The theme toggle is dropped — theme is controlled centrally and propagated to every embedded app.
- All `href`/`src`/`action` paths stay **relative** (no leading `/`), because pages mount under `/{prefix}/{slug}/` and absolute paths would 404.

The release workflow always builds headless. You rarely invoke it directly — the
[release](#publishing-a-release) step handles it.

## marketplace.json

`marketplace.json` at the repo root is the contract between your app and the Knowledge
Base. The build copies it into `dist.tar.gz`, optionally writing a `dist/marketplace.json`
with a computed `pages` array.

### Required fields

| Field | Type | Constraint | Meaning |
|---|---|---|---|
| `marketplaceVersion` | string | `"1"` | Contract version. |
| `name` | string | 2–64 chars | App name shown on the catalog card. |
| `slug` | string | `^[a-z0-9-]+$`, 2–32 chars | URL-safe ID. Pages mount at `/{prefix}/{slug}/`. Must be unique across the Knowledge Base. |
| `description` | string | 10–280 chars | Short blurb on the catalog card. |
| `entryPoint` | string | default `index.html` | Landing page, relative to `dist/`. |

### Optional fields

| Field | Type | Constraint | Meaning |
|---|---|---|---|
| `icon` | string | enum | Catalog-card icon. One of: `book-open`, `cube`, `chip`, `chart-bar`, `shield`, `cog`, `terminal`, `globe`, `layers`, `lightning-bolt`, `document`, `collection`, `puzzle`, `database`. |
| `tags` | array | ≤5 items, each ≤32 chars | Taxonomy pills on the card. |
| `pages` | array | see below | Navigation manifest. When present, it is the authoritative page list (the Knowledge Base does not crawl the filesystem). |

### Pages manifest

Each entry in `pages[]`:

```json
{
  "title": "Getting Started",
  "path": "docs/getting-started/index.html",
  "order": 2,
  "section": "Guides"
}
```

| Field | Required | Meaning |
|---|---|---|
| `title` | yes | Sidebar label (1–128 chars). |
| `path` | yes | HTML path relative to `dist/`. |
| `order` | yes | Sort key (integer ≥0). |
| `section` | no | Sidebar group heading (≤64 chars). |

You do **not** write `pages` by hand. The build generates it from each page's
frontmatter (`title`, `order`, `section`) — the same frontmatter that drives
[auto-navigation](adding-pages.md). Keep your frontmatter correct and the manifest
follows.

## Build pipeline

`scripts/pack.py` (and the `scripts/pack.sh` equivalent) run these steps:

1. Install deps from `requirements.txt` (skip with `SKIP_PIP_INSTALL=1`).
2. Auto-generate nav from `docs/` frontmatter (`title`, `order`, `section`).
3. Write a merged, temporary `mkdocs-build.yml` (headless variant inherits it and sets `extra.headless: true`).
4. Run `mkdocs build` against the merged config → `dist/docs/`.
5. Render `showcase.html` from `data/showcase.yml` → `dist/index.html` (headless strips the `<nav>`).
6. Copy `showcase.css` into `dist/`.
7. Write `dist/marketplace.json` with the computed `pages` manifest.
8. Package `dist/` + `marketplace.json` into `dist.tar.gz`.

Temporary configs (`mkdocs-build.yml`, `mkdocs-headless-build.yml`) are removed on exit.

## Publishing a release

The Knowledge Base pulls from **GitHub Releases**, not from your default branch. Publish
by pushing a semver tag:

```bash
git tag v1.0.0
git push --tags
```

The `Release` workflow (`.github/workflows/pack.yml`) then:

1. Checks out the repo.
2. Installs dependencies.
3. Validates `marketplace.json` has the required fields.
4. Runs the headless build (`bash scripts/pack.sh --headless`).
5. Verifies `dist/index.html`, `dist/docs/index.html`, and the `data-mp-headless="true"` marker exist.
6. Packages `dist.tar.gz` and attaches it to a GitHub Release named for the tag.

You can also trigger it manually via **workflow_dispatch**, supplying the tag as input.

## Registering with the Knowledge Base

The Knowledge Base maintains an `apps.json` registry. To list your app, add an entry
**in the Knowledge Base repo** (not here):

```json
{
  "repo": "AbsaOSS/your-docs-repo",
  "slug": "your-app",
  "name": "Your App Documentation",
  "description": "What this app documents.",
  "icon": "book-open",
  "tags": ["guide", "reference"],
  "version": "latest"
}
```

- `version: "latest"` always pulls the newest release; pin a specific tag (`"v1.2.3"`) to freeze a version.
- The `slug` here should match your `marketplace.json` `slug`.

On its next build the Knowledge Base downloads your latest `dist.tar.gz`, extracts it to
`apps/{slug}/`, rewrites internal links to `/{prefix}/{slug}/…`, injects shared chrome,
and serves the result. Push a new tag and the next Knowledge Base build picks it up.

---

> **Recap:** keep frontmatter and `marketplace.json` accurate → push a `v*` tag → the
> release workflow publishes `dist.tar.gz` → the Knowledge Base aggregates it. No manual
> nav or page-list editing required.

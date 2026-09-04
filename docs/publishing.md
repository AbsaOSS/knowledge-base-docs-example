---
title: Publishing to the Knowledge Base
order: 5
---

# Publishing to the Knowledge Base

This page explains how a docs app is **built**, **packed** into a release artifact and
how the Knowledge Base picks it up and serves it under a shared URL.

You author Markdown; the build script produces a self-contained headless static site
and keeps the manifest in sync. A reusable GitHub Action validates both against the
knowledge base contract, packs them and attaches the result to your GitHub Release.
The Knowledge Base downloads that artifact, rewrites its links, wraps it in shared
chrome, and serves it at `/knowledge-base/{slug}/`.

## The release artifact

Every release carries a single asset: **`kb-docs.tar.gz`**. It contains the manifest at
the root and one directory per app, named after its `slug`. This template publishes one
app, so the archive looks like this:

```
kb-docs.tar.gz
├── kb-docs.json            ← manifest (name, slug, description, pages, …)
└── user-guide/             ← the built dist/, renamed after the slug
    ├── index.html          ← showcase landing (entryPoint)
    ├── docs/
    │   ├── index.html      ← rendered Markdown pages
    │   ├── <page>/index.html
    │   └── style.css
    └── showcase.css
```

The name is `kb-docs.tar.gz`, not `dist.tar.gz`: a docs bundle is not the repo's own
distribution package, and a release often carries both.

You do not assemble the archive by hand and the build script does not produce it either.
Packing is the job of the publish action (see [Publishing a release](#publishing-a-release)).
To inspect what the Knowledge Base will receive without cutting a release, pack locally
with the same layout and deterministic metadata the action uses:

```bash
python scripts/pack.py --pack     # or: bash scripts/pack.sh --pack
```

Output lands at the repo root as `kb-docs.tar.gz`. `--pack` also runs the same
pre-flight checks as the action (headless marker, relative paths, `pages` exist).

## Headless builds

The Knowledge Base embeds your pages **inside its own chrome** (masthead, Library
navigation). To avoid a doubled header and broken layout, apps publish a **headless**
build.

Headless mode (`--headless`) changes the output so it embeds cleanly:

- The site `<header>` (logo + top nav) is omitted — the Knowledge Base supplies the masthead.
- `data-kb-headless="true"` is set on `<html>` of every page so the Knowledge Base can verify the page is headless.
- The theme toggle and dark-mode bootstrap are dropped — the Knowledge Base is light only.
- The CMS under `admin/` is not copied into `dist/` — it is not documentation.
- All `href`/`src`/`action` paths stay **relative** (no leading `/`), because pages mount under `/knowledge-base/{slug}/` and absolute paths would 404.

The release workflow always builds headless. You rarely invoke it directly.

## kb-docs.json

`kb-docs.json` at the repo root is the contract between your app and the Knowledge Base.
It is version 1 of the contract (`kbVersion: "1"`), and it lists every app the release
publishes — for this template, exactly one:

```json
{
  "kbVersion": "1",
  "apps": [
    {
      "slug": "user-guide",
      "name": "Knowledge Base User Guide",
      "description": "Everything you need to publish your own documentation.",
      "icon": "book-open",
      "tags": ["guide", "getting-started", "template"],
      "entryPoint": "index.html",
      "pages": [ "…generated at build time…" ]
    }
  ]
}
```

### Top level

| Field | Required | Meaning |
|---|---|---|
| `kbVersion` | yes | Contract version, as a string. `"1"` today. |
| `apps` | yes | Non-empty list, one entry per app. |

### Each app

| Field | Required | Constraint | Meaning |
|---|---|---|---|
| `slug` | yes | `^[a-z0-9]+(-[a-z0-9]+)*$`, 2–32 chars | Names the directory in the archive and the public URL `/knowledge-base/{slug}/`. Must be unique across the whole Knowledge Base — prefix it with your service name. |
| `name` | yes | 2–64 chars | App name shown on the catalog card and in the masthead. |
| `description` | yes | 10–280 chars | One sentence, shown on the catalog card. |
| `entryPoint` | no | default `index.html` | Landing page, relative to the app directory. |
| `icon` | no | enum | One of: `book-open`, `cube`, `chip`, `chart-bar`, `shield`, `cog`, `terminal`, `globe`, `layers`, `lightning-bolt`, `document`, `collection`, `puzzle`, `database`. |
| `tags` | no | ≤5 items, each ≤32 chars | Taxonomy pills on the card. |
| `pages` | no | see below | Navigation manifest. When present, it is the authoritative route list and the Knowledge Base does not crawl the directory. |

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
| `path` | yes | HTML path relative to the app directory. Must exist in the archive. |
| `order` | yes | Sort key (integer ≥0). |
| `section` | no | Sidebar group heading (≤64 chars). |

You do **not** write `pages` by hand. Every build rewrites `apps[0].pages` in
`kb-docs.json` from each page's frontmatter (`title`, `order`, `section`) — the same
frontmatter that drives [auto-navigation](adding-pages.md). The rest of the file is
never touched. Keep your frontmatter correct and the manifest follows; commit the
result so the file in the repo matches what was last built.

## Build pipeline

`scripts/pack.py` (and the `scripts/pack.sh` equivalent) run these steps:

1. Install deps from `requirements.txt` (skip with `SKIP_PIP_INSTALL=1`).
2. Auto-generate nav from `docs/` frontmatter (`title`, `order`, `section`).
3. Write a merged, temporary `mkdocs-build.yml` (headless variant inherits it and sets `extra.headless: true`).
4. Run `mkdocs build` against the merged config → `dist/docs/`.
5. Render the showcase from `data/showcase.yml` → `dist/index.html` (headless strips the `<nav>` and adds the headless marker).
6. Copy `showcase.css` into `dist/` (and `admin/` for standalone builds only).
7. Write the computed `pages` list into `apps[0].pages` of `kb-docs.json`.
8. With `--pack` only: verify `dist/` against the headless rules and pack `kb-docs.tar.gz`.

Temporary configs (`mkdocs-build.yml`, `mkdocs-headless-build.yml`) are removed on exit.

## Publishing a release

The Knowledge Base pulls from **GitHub Releases**, not from your default branch. The
publish action attaches to an existing release, so publish one — the tag is created if
it does not exist yet:

```bash
gh release create v2.0.0 --generate-notes
```

Or create it in the GitHub UI under **Releases → Draft a new release**. Pushing a tag on
its own does not publish anything.

The `Publish docs` workflow (`.github/workflows/pack.yml`) runs on `release: published`
and is deliberately minimal — this repo is the template every packaged docs repo copies:

```yaml
permissions:
  contents: write        # the action uploads a release asset

steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with: { python-version: "3.12" }
  - run: python scripts/pack.py --headless
  - uses: AbsaOSS/knowledge-base/actions/publish-docs@v1
    with:
      manifest: kb-docs.json
      dist: dist
```

The action then:

1. Validates `kb-docs.json` against the contract schema.
2. Verifies every built HTML file: `data-kb-headless="true"` present, no `<base>`, no root-relative URLs, every `pages` entry and the `entryPoint` exist.
3. Packs `kb-docs.json` + `user-guide/` into `kb-docs.tar.gz` (deterministic: same input, same bytes).
4. Uploads it to the release that triggered the workflow, replacing any existing asset.

Every problem is reported at once, naming the file, so a broken build costs one CI round
trip rather than five. You can also run the workflow manually via **workflow_dispatch**,
optionally naming an existing release to attach to (defaults to the latest).

Pin the action to a major tag (`@v1`), not to a branch. A breaking contract change ships
as `@v2` together with a `kbVersion` bump, so a pinned major keeps publishing until you
choose to move.

Once a deployment repository exists, the optional `notify-repo` / `notify-token` inputs
(commented out in the workflow) fire a `repository_dispatch` so the deployment rebuilds
without waiting for its schedule.

## Registering with the Knowledge Base

The Knowledge Base maintains an `apps.json` registry. To list your app, open a PR
**in the Knowledge Base repo** (not here) adding one entry:

```json
{ "repo": "AbsaOSS/your-docs-repo", "version": "latest" }
```

That is the whole entry. Name, description, icon, tags, slug and pages are all read from
your `kb-docs.json`, so adding, renaming or removing a doc later never touches the
Knowledge Base repository again.

- `version: "latest"` always pulls the newest release; pin a specific tag (`"v1.2.3"`) to freeze a version.

On its next build the Knowledge Base downloads your latest `kb-docs.tar.gz`, extracts
`user-guide/` (your slug), rewrites internal links to `/knowledge-base/{slug}/…`, injects
shared chrome, and serves the result. Publish a new release and the next Knowledge Base
build picks it up.

---

> **Recap:** keep frontmatter and `kb-docs.json` accurate → publish a GitHub Release →
> the publish action attaches `kb-docs.tar.gz` → the Knowledge Base aggregates it. No
> manual nav or page-list editing required.

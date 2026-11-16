---
title: Building
order: 41
section: Run a Knowledge Base
---

# Building

Requires **Node.js 24 or newer**. A GitHub fetch needs `GITHUB_TOKEN` (or an
authenticated `gh` CLI).

```bash
npm install
npm run build:headless        # hermetic: builds from the committed registry fixtures
```

## Build modes

| Command | Source of apps |
|---|---|
| `npm run build` | Fetch GitHub Release artifacts |
| `npm run build:headless` | Same, with web-fragment output |
| `npm run build:local` | Build `localPath` entries from local checkouts |
| `npm run build:local:headless` | Local, headless |
| `npm run preview` | Serve the built `dist/` (Astro preview, port 4321) |
| `npm run dev` | Astro dev server; needs artifacts in `apps/` already |
| `npm run dev:fetch` | Fetch artifacts, then start dev |

| Flag | Environment variable | Effect |
|---|---|---|
| `--headless` | `KB_HEADLESS=true` | Web-fragment output: `data-kb-headless="true"` on `<html>`. Anything else, including unset, is standalone. A per-app `headless` in the registry wins. |
| `--strict` | `KB_STRICT=true` | Production mode; see below. |
| `--local` | — | A `repo` entry without a `localPath` is skipped with a warning. |

Other environment variables:

| Variable | Description |
|---|---|
| `GITHUB_TOKEN` | Auth for fetching Release artifacts. |
| `KB_REGISTRY` | Registry file to build from. Default `apps.json`. See [Registry](registry.md). |

The URL prefix `knowledge-base` is **not** configurable. nginx and the gateway route
patterns hard-code the same string.

### Strict mode

`--strict` / `KB_STRICT=true` is for production. It rejects `prebuilt`, `localPath` and
`optional` entries, an empty registry, any entry that yields no apps, and any artifact
with an `error` finding from the [contract checker](rules.md). Warnings never fail a
build. The registry committed in the Knowledge Base repository is a fixture and fails
strict mode by design.

## Pipeline

1. Stage each artifact and install its apps into `apps/{slug}/`. Archives are extracted
   safely: no traversal, absolute paths or links ([archive rules](manifest.md#the-archive)).
2. Run the contract checks and log findings grouped by rule.
3. Hoist inline `<script>` bodies into `_kb-inline/*.js` files.
4. Copy non-HTML assets; wrap sub-app CSS in the `kb-app` layer.
5. Build the static site into `dist/`.

## Output

`dist/` is the whole site. It also holds:

| File | Purpose |
|---|---|
| `style.css` | The Knowledge Base stylesheet under a stable name. Pages inline it themselves. |
| `kb-build.json` | Provenance: what the build was assembled from. |

`kb-build.json` looks like this:

```json
{
  "builtAt": "2026-09-04T13:44:49.043Z",
  "registry": "apps.json",
  "strict": true,
  "headless": true,
  "sources": [
    { "source": "AbsaOSS/my-service-docs", "version": "v1.4.0", "slugs": ["my-service"] }
  ],
  "iframes": []
}
```

This answers "which release produced this page", which a `latest` registry entry cannot
once it has moved. In GitHub Actions the same table is written to the job summary.

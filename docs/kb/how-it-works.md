---
title: How it works
order: 10
section: Knowledge Base
---

# How the Knowledge Base works

The Knowledge Base is a build-time aggregator. A **registry** (`apps.json`) lists where
each team's documentation comes from; the build collects it and produces one static
`dist/`.

```
Browser ──► /knowledge-base/                 landing catalog
            /knowledge-base/{slug}/…         each documentation app
            /__wf/knowledge-base/…           assets when embedded as a web fragment
                  │
                  ▼
       nginx (Docker)  ─or─  web-fragments gateway (embedded)
                  │
                  ▼
              dist/  (static)
```

## The build, step by step

1. **Obtain** each registered artifact: a GitHub Release asset (`kb-docs.tar.gz`), a
   local checkout, or a prebuilt tarball or directory. See [Registry](registry.md).
2. **Read the manifest** (`kb-docs.json`) inside each artifact. It declares one or
   more apps with their slug, name, description, icon, tags and pages. See
   [The manifest](manifest.md).
3. **Check** every artifact against the [contract rules](rules.md) and log the findings.
4. **Move inline scripts into files** so the site can be served with `script-src 'self'`.
5. **Re-host every page**: rewrite URLs, wrap CSS, wrap the page in the masthead.
6. **Generate the catalog** landing page.

The output makes no third-party requests at runtime: the Inter typeface is self-hosted
and mermaid is vendored into each single-page artifact.

## Reading the portal

- **Masthead** — shown on every page. It carries the branding and a *Library* link
  plus the current app's navigation.
- **Catalog** — the landing page at `/knowledge-base/`, one card per app showing its
  name, description, icon and tags. Apps registered as an `iframe` entry carry an
  **External** badge.
- **App pages** — each app keeps its own sidebar, routing and internal navigation.
  Single-page docs render in a centred reading column with no sidebar.
- **Light only** — there is no dark mode and no theme toggle.

## What happens to your HTML

Artifacts come from other repositories, so their HTML is treated as untrusted input.
When a page is re-hosted:

- Every `href`, `src`, `action`, `formaction` and `poster` URL (and `srcset`, `url()`
  in styles, and URL-bearing `<meta>` content) is rewritten to an absolute
  `/knowledge-base/{slug}/…` path. A `<base>` element is removed.
- Each sub-app stylesheet is wrapped in the `kb-app` CSS cascade layer, below the
  Knowledge Base's own rules, so a docs theme cannot restyle the masthead or catalog.
  `!important` defeats this (KB-CSS-001 in [Contract rules](rules.md)).
- Inline `on*` event handlers are removed, and so are a theme bootstrap script and a
  `dark` class on `<html>`/`<body>`.
- Inline `<script>` bodies are hoisted into files at build time.

Each of these maps to a rule in [Contract rules and the checker](rules.md); following
the rules at the source means the page you wrote is the page readers get.

## Who does what

| You are… | Read |
|---|---|
| Publishing docs | [Choosing how to onboard](onboarding.md) |
| Running the portal | [Registry](registry.md), [Building](building.md), [Deployment](deployment.md) |
| Embedding it in an app | [Web fragment embedding](embedding.md) |

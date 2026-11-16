---
title: Packaged docs
order: 22
section: Publish Your Docs
---

# Packaged docs

If you have a real static docs site, publish it as a **headless** build with a
`kb-docs.json` manifest. This guide is built that way from the
[Docs Template](../template.md).

## What you need

1. A **headless build** of your site.
2. A [`kb-docs.json`](manifest.md) at the repo root.
3. A release workflow calling the `publish-docs` action.

### 1. The headless build

Your build must support a headless variant (conventionally a `--headless` flag):

```bash
npm run build -- --headless   # used by the release workflow
npm run build                 # standalone, for local preview
```

When headless:

| Requirement | Detail |
|---|---|
| No site-level `<header>` | Omit the fixed top bar with logo and main links. The Knowledge Base supplies the masthead. |
| `data-kb-headless="true"` | On the `<html>` element of every page. |
| No theme toggle | The Knowledge Base is light only. |
| Relative paths | Every `href`, `src` and `action` is relative, with no leading `/`. Apps mount at `/knowledge-base/{slug}/`. |
| Sidebar offset | Sidebar `top` is `0`; nothing is reserved above your content. |
| No `<base>` element | It would re-resolve every relative URL. |

Expected body structure:

```html
<body>
  <nav id="sidebar" aria-label="Documentation">…</nav>
  <main id="content">…</main>
</body>
```

### Scripts as files

The deployment serves `script-src 'self'`. Ship scripts as `<script src>`: inline
`on*` handlers are stripped, inline `<script>` blocks are hoisted into files at build
time, and `javascript:` URLs are blocked. See the HTML rules in
[Contract rules](rules.md#html).

### Design tokens

Your CSS must define the canonical design tokens. See [Style tokens](style-tokens.md).

### 2. The release workflow

```yaml
# .github/workflows/publish-docs.yml
name: Publish docs

on:
  release:
    types: [published]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build -- --headless   # whatever your generator is
      - uses: AbsaOSS/knowledge-base/actions/publish-docs@v1
        with:
          manifest: kb-docs.json
          dist: dist
```

The action validates the manifest, checks the HTML against the [rules](rules.md), packs
the [archive](manifest.md#the-archive) and uploads it. Inputs are in
[Actions](actions.md#publish-docs). Pin it to a major tag (`@v1`).

### 3. Register

Open a PR adding `{ "repo": "owner/name", "version": "latest" }` to the deployment's
registry. See [Choosing how to onboard](onboarding.md#the-two-steps-every-type-shares).

## Checklist

- [ ] `kb-docs.json` is in the repo root and validates against the schema
- [ ] The headless build succeeds and writes the directory named in the workflow
- [ ] That directory contains `index.html` (or your `entryPoint`)
- [ ] No site-level `<header>` in any page; `data-kb-headless="true"` on `<html>`
- [ ] All asset paths are relative; no `on*` attributes
- [ ] Design tokens are defined in your CSS
- [ ] A release carries `kb-docs.tar.gz`
- [ ] Locally, the [checker](rules.md#running-the-checks) reports no errors

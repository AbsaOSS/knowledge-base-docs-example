---
title: Single-page docs
order: 21
section: Publish Your Docs
---

# Single-page docs

The zero-config way in. Your repo has one or more Markdown files; you add **one
workflow file and nothing else**. The `publish-single-page-docs` action renders the
Markdown into headless HTML, packs it as `kb-docs.tar.gz`, and attaches it to a release.
Each doc gets its own catalog card and URL.

## 1. Add the workflow

```yaml
# .github/workflows/publish-docs.yml
name: Publish docs

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: write        # the action uploads a release asset
    steps:
      - uses: actions/checkout@v4
      - uses: AbsaOSS/knowledge-base/actions/publish-single-page-docs@v1
        with:
          docs: |
            - md: docs/overview.md
              title: Service Overview
              description: What the service does and how to use it.
              slug: my-service
```

Multiple docs go in the same list. Add `icon` and `tags` where useful.

### Each doc definition

| Field | Required | Rules |
|---|---|---|
| `md` | yes | Path to the Markdown file, relative to the repo root. Must exist in the checkout. |
| `title` | yes | Catalog card and masthead title. At most 128 characters. Becomes the app `name`. |
| `description` | yes | One sentence for the card. 10–280 characters. |
| `slug` | yes | Lowercase kebab-case, 2–32 characters. Becomes the URL `/knowledge-base/{slug}/` and must be unique across the whole Knowledge Base, so prefix it with your service name. |
| `icon` | no | One of the [icon set](manifest.md#icon-set). Default `book-open`. |
| `tags` | no | Up to 5 short strings. |

Validation runs before anything is rendered and reports every problem at once.
Inputs and outputs of the action are listed in [Actions](actions.md#publish-single-page-docs).

## 2. Publish a release and register

The action never creates a release; it attaches to one. Trigger it on
`release: published`. Then [register the repo](onboarding.md#the-two-steps-every-type-shares).

## What the action produces

- **Markdown**: GitHub-flavoured — tables, task lists, strikethrough, footnotes,
  autolinked URLs (external links open in a new tab with `rel="noopener noreferrer"`),
  heading anchors on `h1`–`h4`, syntax-highlighted code, and `mermaid` code blocks
  rendered client-side from a vendored mermaid bundle.
- **Heading**: if the Markdown has no top-level `#` heading, one is synthesised from
  `title` and `description`.
- **Layout**: each doc is a single `<article class="kb-doc">` with scoped styles. The
  Knowledge Base renders it in a centred reading column with no sidebar.

### Raw HTML

Raw HTML in Markdown is passed through an allowlist, because your doc is served on the
same origin as everyone else's.

| Dropped (inner text kept) | Why |
|---|---|
| `<script>` | Would run on the Knowledge Base origin |
| `on*` attributes | Same |
| `<style>` and `style="…"` | CSS can exfiltrate via `url()` or cover the masthead |
| `<iframe>`, `<object>`, `<embed>` | Arbitrary embedded documents |
| `<form>` and form controls (except task-list checkboxes) | Phishing surface |
| `javascript:` and `data:` URLs | Script execution |

Structural and inline elements (headings, lists, tables, `details`/`summary`, `figure`,
`blockquote`, `pre`/`code`, `img`, `a`, emphasis) are kept with their `class` and `id`.
There is no opt-out: a doc that needs inline scripting should be [packaged](packaged.md).

## Troubleshooting

| Message | Cause |
|---|---|
| `has no GitHub Release to attach the docs bundle to` | The repo has no releases. Create one, or pass `release-tag`. |
| `md "…" does not exist in the repository` | Wrong path, or `actions/checkout` is missing. |
| `slug "…" is invalid` | Slugs are lowercase kebab-case: no underscores, capitals or spaces. |
| `Duplicate app slug "…"` (in the Knowledge Base build) | Another app already owns that URL. Rename yours and republish. |
| `npm error … ENOTFOUND registry.npmjs.org` | The runner cannot reach the public registry. See [Private networks](private-networks.md). |

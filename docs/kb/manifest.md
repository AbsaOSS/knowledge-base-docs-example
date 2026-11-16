---
title: The manifest and archive
order: 23
section: Publish Your Docs
---

# The manifest and archive

Every app the Knowledge Base serves is a directory in `kb-docs.tar.gz` plus an entry in
`kb-docs.json`. A repo publishing one docs site lists one app; a repo publishing several
Markdown docs lists several. Normative sources:
[ARTIFACT.md](https://github.com/AbsaOSS/knowledge-base/blob/v1.3.1/contract/ARTIFACT.md) and
[kb-docs.schema.json](https://github.com/AbsaOSS/knowledge-base/blob/v1.3.1/contract/kb-docs.schema.json).

```json
{
  "kbVersion": "1",
  "apps": [
    {
      "slug": "user-guide",
      "name": "Knowledge Base User Guide",
      "description": "Everything you need to publish your own documentation.",
      "icon": "book-open",
      "tags": ["guide", "getting-started"],
      "entryPoint": "index.html",
      "pages": [
        { "title": "Overview",   "path": "index.html",                 "order": 1 },
        { "title": "Publishing", "path": "docs/publishing/index.html", "order": 2, "section": "Guide" }
      ]
    }
  ]
}
```

The file is UTF-8 without a BOM.

## Top level

| Field | Required | Description |
|---|---|---|
| `kbVersion` | yes | Contract version as a **string**. `"1"` today. A Knowledge Base that does not understand it fails the build. |
| `apps` | yes | Non-empty array, one entry per app. |

No other top-level fields are allowed by the schema.

## Each app

| Field | Required | Default | Rules |
|---|---|---|---|
| `slug` | yes | — | `^[a-z0-9]+(-[a-z0-9]+)*$`, 2–32 characters. Names the archive directory and the URL `/knowledge-base/{slug}/`. Unique across the whole Knowledge Base; prefix it with your service name. |
| `name` | yes | — | 2–64 characters. Shown on the card and in the masthead. |
| `description` | yes | — | 10–280 characters. One sentence, shown on the card. |
| `entryPoint` | no | `index.html` | Landing page relative to `<slug>/`. Relative, forward-slashed, no `..`. |
| `icon` | no | `book-open` | One of the [icon set](#icon-set). An unknown value falls back to `book-open`. |
| `tags` | no | none | Up to 5 strings, each 1–32 characters. |
| `pages` | no | crawl | Navigation manifest; see below. |

### Icon set

`book-open`, `cube`, `chip`, `chart-bar`, `shield`, `cog`, `terminal`, `globe`,
`layers`, `lightning-bolt`, `document`, `collection`, `puzzle`, `database`.

### `pages`

When present, `pages` is the **authoritative** route list: the Knowledge Base serves
exactly these and does not crawl. Omit it and every HTML file under `<slug>/` becomes a
route with a title derived from the document.

| Field | Required | Rules |
|---|---|---|
| `title` | yes | 1–128 characters. |
| `path` | yes | HTML path relative to `<slug>/`. Must exist in the archive. |
| `order` | yes | Integer ≥ 0; lower sorts higher. |
| `section` | no | 1–64 characters. Group heading above the page. |

A page whose file is missing fails the build rather than producing a route that 404s.
This guide, built from the [Docs Template](../publishing.md), writes `pages` for you
from page frontmatter.

### Versioning

Additive changes (a new optional field) do not change `kbVersion`; unknown fields are
ignored by the Knowledge Base, so validate against the schema rather than trusting it to
catch a typo. A breaking change bumps the major and ships as a new major tag of the
actions ([Actions](actions.md#versioning)).

## The archive

```
kb-docs.tar.gz
├─ kb-docs.json
├─ <slug-a>/
│  ├─ index.html          ← entryPoint
│  └─ assets/…
└─ <slug-b>/              ← only a bundle with several apps
```

The asset is called `kb-docs.tar.gz`, not `dist.tar.gz`. You do not assemble it by
hand; the [publish actions](actions.md) do.

The archive is untrusted input. Extraction is refused if any member is an absolute path
or carries a drive letter, contains a `..` segment, is a symbolic or hard link, or is
anything other than `kb-docs.json` or a path under a `<slug>/` directory named in the
manifest. A member under an undeclared directory is ignored with a warning. A
`kb-docs.json` under a single `dist/` wrapper is also accepted.

### Size

| Size | Result |
|---|---|
| ≤ 20 MB | Target |
| > 20 MB | Warning ([KB-ART-004](rules.md#manifest-and-artifact)); the build names the app |
| > 100 MB | Refused ([KB-ART-005](rules.md#manifest-and-artifact)); also GitHub's per-asset limit |

Uncompressed images and vendored toolchains are the usual cause of a large artifact.

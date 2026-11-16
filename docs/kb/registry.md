---
title: Registry
order: 40
section: Run a Knowledge Base
---

# The registry

The registry is a JSON array saying **where** each artifact comes from. What an artifact
*is* comes from its own [`kb-docs.json`](manifest.md). By default the file is
`apps.json`; set `KB_REGISTRY` to use another one (relative to the project root, or
absolute) — which is how a [deployment repository](deployment.md) owns its own list.

```json
[
  { "repo": "AbsaOSS/my-service", "version": "latest" },
  { "repo": "AbsaOSS/platform-docs", "version": "v2.1.0" },
  { "localPath": "../my-docs" },
  { "prebuilt": "tests/fixtures/my-docs.kb-docs.tar.gz" },
  { "type": "iframe", "slug": "legacy", "url": "https://docs.example.com", "name": "Legacy docs",
    "description": "Docs hosted elsewhere.", "temporary": true }
]
```

## Sources

An entry names exactly one source.

| Field | Meaning |
|---|---|
| `repo` | `owner/name`. The build downloads `kb-docs.tar.gz` from that repository's release. |
| `version` | With `repo` only. `latest` (default) or a pinned tag such as `v1.4.0`. |
| `prebuilt` | Path to a tarball or an unpacked directory. For hermetic, offline builds. |
| `localPath` | Path to a local checkout. The build runs its pack command, then reads `kb-docs.tar.gz` from the checkout root. |
| `pack` | With `localPath` only. Command to run (default `npm run pack:kb`), or `false` to skip when the artifact is already built. |

Pin a tag for anything that must not move without review. Rolling back is then a
one-line change.

## Options

| Field | Applies to | Meaning |
|---|---|---|
| `headless` | any artifact entry | `true`/`false` pins one app against the build flag. A per-app value wins over `--headless`/`KB_HEADLESS`. |
| `optional` | `prebuilt`, `localPath` | `true` skips the entry with a warning when its artifact is missing, instead of failing. Not allowed on `repo` entries. |

## Entries are source-only

An artifact entry must **not** set `slug`, `name`, `description`, `icon`, `tags`,
`entryPoint` or `pages`, nor `type`: the build rejects it and says to move the field to
`kb-docs.json`. A `version` without `repo`, or a `pack` without `localPath`, is also
rejected.

## iframe entries

`type: "iframe"` entries embed an external site; they are the only entries that carry
display fields.

| Field | Required | Description |
|---|---|---|
| `type` | yes | `"iframe"`. |
| `slug` | yes | Lowercase kebab-case. |
| `url` | yes | Site to embed. Must not set `repo`, `prebuilt` or `localPath`. |
| `name`, `description`, `icon`, `tags` | no | Catalog card content. |
| `temporary` | no | Marks a stopgap; the build warns. |

The external site's `frame-ancestors` / `X-Frame-Options` must permit framing. The
nginx policy allows `https:` frames ([Docker and nginx](docker-nginx.md)).

## Strict builds

In a [strict build](building.md#build-modes), `prebuilt`, `localPath` and `optional` are
rejected, as are an empty registry and any entry that produces no apps.

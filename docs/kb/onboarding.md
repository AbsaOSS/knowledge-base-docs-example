---
title: Choosing how to onboard
order: 20
section: Publish Your Docs
---

# Choosing how to onboard

There are three ways to get documentation into the Knowledge Base.

| Type | Use when | Cost to your repo |
|---|---|---|
| **Single-page** | You have Markdown files, not a docs *site* | One workflow file. See [Single-page docs](single-page.md). |
| **Packaged** (default) | You have a real static docs site (MkDocs, Starlight…) | A headless build, `kb-docs.json` and a release workflow. See [Packaged docs](packaged.md). |
| **iframe** | Your docs are hosted elsewhere and cannot be packaged yet | An `apps.json` entry in the deployment's registry. An explicit stopgap. |

When both single-page and packaged would fit, prefer single-page: it is one file, it is
reversible, and you can move to packaged later without touching the Knowledge Base.

This guide is itself a packaged site, built with the [Docs Template](../template.md).

## The two steps every type shares

1. **Publish a GitHub Release.** A workflow in your repo builds the artifact and
   attaches `kb-docs.tar.gz` to it. The actions attach to an existing release and
   never create one.
2. **Register the repo** with a pull request to the deployment's `apps.json`:

   ```json
   { "repo": "AbsaOSS/my-service", "version": "latest" }
   ```

   That is the whole entry. Everything else is read from your `kb-docs.json`, so later
   changes never touch the registry. `version` accepts `latest` (the default) or a
   pinned tag such as `v1.4.0`. See [Registry](registry.md).

## iframe entries

A team that already hosts its docs elsewhere can be listed immediately with an
`iframe` entry in the registry. It renders a full-viewport `<iframe>` below the
masthead and shows an **External** badge in the catalog. This is the one entry kind
that carries display fields, because there is no manifest to read them from:

```json
{
  "type": "iframe",
  "url": "https://my-team.example.com/docs",
  "slug": "my-team",
  "name": "My Team Docs",
  "description": "Documentation for My Team's services.",
  "icon": "book-open",
  "tags": ["my-team"],
  "temporary": true
}
```

`type`, `slug` and `url` are required. The external site must allow framing: its
`frame-ancestors` / `X-Frame-Options` must not block the Knowledge Base origin.
`temporary: true` marks the entry as a stopgap; migrate to a packaged artifact when
you can.

## Using an AI agent

The [`kb-docs-add` skill](agent-skill.md) picks the type for you and writes only the
files the contract requires.

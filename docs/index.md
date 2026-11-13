---
title: Overview
order: 1
---

# Knowledge Base

The Knowledge Base is a **build-time aggregator** for static documentation sites.
Each team keeps its docs in its own repository; the Knowledge Base collects them
into one portal served under `/knowledge-base/`, with a shared masthead and a
catalog landing page listing every registered app.

At build time it:

1. Obtains each registered app's built output — a GitHub Release artifact
   (`kb-docs.tar.gz`), a local checkout, or a prebuilt tarball or directory.
2. Rewrites every page's URLs to `/knowledge-base/{slug}/…` and wraps each page
   in the Knowledge Base masthead.
3. Generates the catalog landing page.
4. Produces a single static `dist/`, served by nginx in Docker or embedded into a
   host application as a web fragment.

The output makes no third-party requests at runtime.

## Who this guide is for

| You want to… | Start with |
|---|---|
| Publish your team's documentation to the Knowledge Base | Publishing your docs |
| Run your own Knowledge Base deployment | Running a Knowledge Base |
| Embed the Knowledge Base inside a host application | Embedding |
| Start a new docs site quickly | [Using the Docs Template](template.md) |

## About this site

This guide is itself published to the Knowledge Base with the
[Docs Template](template.md) it describes, so it doubles as a working example of
a packaged documentation app.

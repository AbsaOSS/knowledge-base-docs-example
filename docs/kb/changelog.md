---
title: Changelog
order: 90
section: Reference
---

# Changelog

User-facing changes per Knowledge Base release that this guide describes.

## v1.3.1 — 2026-11-06

First release documented by this guide (initial sync), so the list below also covers
the behaviour the guide now describes in full.

- Inline `on*` event handlers in docs HTML are stripped when pages are re-hosted
  ([How it works](how-it-works.md), rule KB-HTML-005 in [Contract rules](rules.md)).
- Scripts swapped in by in-fragment navigation now run inside the fragment, and sub-app
  styles no longer flash on navigation ([Web fragment embedding](embedding.md)).
- nginx caches hashed assets as `immutable` and revalidates everything else
  ([Docker and nginx](docker-nginx.md#caching)).
- The image build can trust a proxy CA for `apk upgrade` and patches base-image CVEs
  ([Private networks](private-networks.md#ca-certificates)).
- Single-page docs keep their list markers ([Single-page docs](single-page.md)).
- The `kb-docs-add` skill frontmatter is valid YAML ([Agent skill](agent-skill.md)).

Features available in this release:

- Three onboarding types: [single-page, packaged and iframe](onboarding.md).
- [Contract rules](rules.md) with stable IDs, the local checker and the `check-docs` PR action.
- [Private-network inputs](private-networks.md) on the actions and the build workflow.
- The [`build-image.yml`](deployment.md) reusable workflow and `kb-build.json` provenance.

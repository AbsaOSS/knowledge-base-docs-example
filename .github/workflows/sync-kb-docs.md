---
description: Opens a draft PR that brings this template's docs in line with a new knowledge-base release

# Fired by AbsaOSS/knowledge-base's release workflow:
#   POST /repos/AbsaOSS/knowledge-base-docs-example/dispatches
#   {"event_type": "kb-release", "client_payload": {"tag": "v1.2.0"}}
on:
  repository_dispatch:
    types: [kb-release]
  workflow_dispatch:
    inputs:
      tag:
        description: 'knowledge-base release tag to sync against (e.g. v1.2.0)'
        required: true
        type: string

permissions:
  contents: read
  issues: read
  pull-requests: read

engine: copilot

timeout-minutes: 20

checkout:
  - fetch-depth: 1
  - repository: AbsaOSS/knowledge-base
    path: ./.kb-upstream
    ref: ${{ github.event.client_payload.tag || github.event.inputs.tag }}
    fetch-depth: 0

network:
  allowed:
    - defaults
    - python

tools:
  github:
    toolsets: [repos]
  edit:
  bash: ["git:*", "ls", "cat", "head", "grep", "find", "diff", "python:*", "pip:*", "node:*"]

safe-outputs:
  create-pull-request:
    title-prefix: "[kb-sync] "
    labels: [documentation, automation]
    draft: true
    if-no-changes: "warn"
---

# Sync docs with a knowledge-base release

AbsaOSS/knowledge-base just released a new version. This repository is the
template that other documentation repositories copy, so its docs, manifest and
build must match the knowledge base contract of that release.

Release tag (one of these is empty): `${{ github.event.client_payload.tag }}` `${{ github.event.inputs.tag }}`

The release is checked out at `./.kb-upstream` with full history.

## 1. Find what changed upstream

1. In `./.kb-upstream`, find the previous `vMAJOR.MINOR.PATCH` tag before the
   release tag (`git tag --sort=-v:refname`).
2. Diff the two tags, limited to the parts this template depends on:
   - `contract/` (especially `ARTIFACT.md`, `HEADLESS_RULES.md`, `RULES.md`, `kb-docs.schema.json`)
   - `actions/publish-docs/action.yml` and `actions/check-docs/action.yml` (inputs, outputs, defaults)
   - `actions/publish-docs/README.md` and `actions/check-docs/README.md`
3. Read the release notes for the tag with the GitHub tools.

If nothing in those paths changed in a way that affects this repository, stop
without making changes.

## 2. Bring this repository in line

Check and update, keeping each change as small as possible:

- `kb-docs.json`: fields, `kbVersion` (only on a major release), anything the schema now requires or forbids
- `docs/*.md`, especially `docs/publishing.md`: described behaviour, action inputs, contract rules
- `README.md` and `CLAUDE.md`: the "Knowledge Base Contract" section and build pipeline notes
- `theme/main.html` and `scripts/pack.py`: only if a headless rule changed
  (for example a required attribute or a forbidden element)

Rules:

- Do not edit anything under `.github/`. If `pack.yml` or `check-docs.yml` need a
  change (for example a new action input or a new major tag like `@v2`), describe
  the exact change in the pull request body instead.
- Do not touch `package-lock.json`, `theme/style.css` or generated files.
- Match the existing tone and structure of each file; do not reformat untouched text.
- Every statement you add must be backed by the upstream diff or release notes.

## 3. Verify

Run `python scripts/pack.py --headless` and make sure it succeeds. If the
upstream checker is usable offline, run
`node ./.kb-upstream/actions/lib/check-cli.js --manifest kb-docs.json --dist dist`
when `node` is available; skip it otherwise and say so.

Do not commit `dist/` or `./.kb-upstream`.

## 4. Open a pull request

Create one pull request. Title: `docs: sync with knowledge-base <tag>`.
The body must contain:

- the upstream tag range compared and a link to the release
- a bullet list of each upstream change and the matching change made here
- any required workflow (`.github/`) change that you did not make
- a `## Release Notes` section with bullet points describing the user-visible changes

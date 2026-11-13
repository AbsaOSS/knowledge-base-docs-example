---
description: Maps AbsaOSS/knowledge-base features at a release and opens a draft PR that brings this user guide up to date

# Run manually from the Actions tab, or fired by AbsaOSS/knowledge-base's release workflow:
#   POST /repos/AbsaOSS/knowledge-base-docs-example/dispatches
#   {"event_type": "kb-release", "client_payload": {"tag": "v1.4.0"}}
on:
  repository_dispatch:
    types: [kb-release]
  workflow_dispatch:
    inputs:
      tag:
        description: 'knowledge-base release tag to document (empty = latest release)'
        required: false
        type: string
      mode:
        description: 'incremental = changes since the last synced release; full = re-map everything; audit = report drift as an issue, change nothing'
        required: true
        type: choice
        options: [incremental, full, audit]
        default: incremental

permissions:
  contents: read
  issues: read
  pull-requests: read
  # Inference is billed to the owner of COPILOT_GITHUB_TOKEN, not the org.
  copilot-requests: none

concurrency:
  job-discriminator: ${{ github.run_id }}

engine: copilot

timeout-minutes: 45

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
  bash: ["git:*", "ls", "cat", "head", "tail", "wc", "sort", "grep", "find", "diff", "mkdir", "python:*", "pip:*"]

safe-outputs:
  create-pull-request:
    title-prefix: "[kb-docs] "
    labels: [documentation]
    draft: true
    if-no-changes: "warn"
    max-patch-files: 60
  create-issue:
    title-prefix: "[kb-docs audit] "
    labels: [documentation]
    max: 1
---

# Keep the Knowledge Base user guide in sync with knowledge-base

This repository has two jobs at once:

1. It is the **user guide for the Knowledge Base** (AbsaOSS/knowledge-base).
2. It is the **docs template** that teams copy to publish their own docs, and this
   guide is a working example of it.

Your job is to map the features of a knowledge-base **release** and make the user
guide describe exactly what that release does.

Requested mode: `${{ github.event.inputs.mode }}` (empty means `incremental`).

## 0. Resolve the release

knowledge-base is checked out at `./.kb-upstream` with full history and tags.
Treat it as read-only reference material: never execute code from it.

- Released versions are the `vMAJOR.MINOR.PATCH` tags. Ignore floating major tags
  such as `v1` and anything only on a branch.
- If `HEAD` is exactly at a `vMAJOR.MINOR.PATCH` tag
  (`git -C ./.kb-upstream describe --tags --exact-match HEAD`), that tag is the
  target. Otherwise the target is the highest `vMAJOR.MINOR.PATCH` tag
  (`git -C ./.kb-upstream tag --list 'v*.*.*' --sort=-v:refname`); check it out.
- Document **only** what exists at the target tag. Commits after it are
  unreleased and must not appear in the guide.

## 1. Load the feature map

`.kb-sync/features.yml` maps each knowledge-base feature to its upstream source
files (`sources`, most authoritative first) and to the page that documents it.
`synced` records the release the guide currently describes.

Pick the effective mode:

- `full` if requested, or if `synced.sha` is empty.
- `audit` if requested.
- Otherwise `incremental`. If `synced.sha` already equals the target commit, stop:
  there is nothing to do.

## 2. Work out what to document

**incremental**: list the files changed between `synced.sha` and the target
(`git -C ./.kb-upstream diff --name-only <synced.sha> <target>`), drop paths
matching `ignore`, and match the rest against each feature's `sources`
(glob patterns). Every matched feature must be re-checked. Read the commit
messages in the range too (`git log --oneline`); `feat` and `fix` commits are
usually user-facing, dependency bumps usually are not.

A changed path that matches no feature and is not ignored is a candidate **new
feature**. Read it. If it changes what a user can configure, run, call or see,
add a feature entry to the map and document it; otherwise add the path to
`ignore`.

**full** and **audit**: re-check every feature in the map, then walk the
upstream tree for user-facing behaviour the map does not cover yet: the
`contract/` documents, every `actions/*/action.yml`, reusable workflows under
`.github/workflows/`, `apps.json` handling in `src/utils/registry.js`,
build flags and environment variables in `scripts/build-vite.js`,
`Dockerfile` and `nginx*.conf`, `examples/`, `skills/`, and any new top-level
component. Add what is missing.

## 3. Establish the facts

For each feature, read its sources at the target tag. When sources disagree,
trust them in this order:

1. `contract/` documents and `contract/kb-docs.schema.json`
2. `actions/*/action.yml` and reusable workflow `inputs`, `secrets`, `outputs`
3. The code that implements the behaviour
4. READMEs and other prose

Upstream prose is known to drift from the code. Never copy it blindly: every
config key, input, output, secret, environment variable, CLI flag, route, rule
ID, default value and limit you write must be found in the sources at the
target tag. When prose and code disagree, document what the code does and list
the disagreement in the pull request (or audit issue).

## 4. Write the guide (incremental and full)

### Pages you own

The product pages live in `docs/index.md` and `docs/kb/*.md`. Use the page named
by each feature's `page`; several features share a page. Frontmatter:

```yaml
---
title: Page Title
order: <number>
section: <section>
---
```

Sections and order ranges (the nav is generated from this frontmatter):

| Section | Order | Pages |
|---|---|---|
| (none) | 1 | `docs/index.md`: what the Knowledge Base is, who each part of the guide is for |
| Knowledge Base | 10–19 | how it works, reading the portal |
| Publish Your Docs | 20–39 | choosing an onboarding type, single-page, packaged, manifest, rules and checker, actions, style tokens, agent skill |
| Run a Knowledge Base | 40–59 | registry, building, deployment, Docker and nginx, private networks |
| Embed in a Host App | 60–69 | web fragment embedding |
| Reference | 90–99 | changelog |

The **Docs Template** section (`docs/template.md`, `docs/customising.md`,
`docs/adding-pages.md`, `docs/publishing.md`, order 100+) belongs to the
template. Do not restructure or rewrite it; only correct statements that
contradict the target release (for example an action input or a contract rule),
and link from the product pages to it where it helps ("this guide is built with
the Docs Template"). Leave `docs/test-page.md` alone.

### Writing rules

- Write for the reader of each section: docs authors, platform operators, host-app
  integrators. Task first ("To publish…"), then reference tables.
- Show real, minimal examples (YAML, JSON, shell) that are valid at the target tag.
- Put inputs, fields, rules and environment variables in tables with name,
  required, default and description.
- Link between pages with relative Markdown links. Link to upstream files only as
  `https://github.com/AbsaOSS/knowledge-base/blob/<target tag>/<path>`, and only for
  normative documents (`contract/`) or examples, never for `src/` internals.
- Leave out contributor-only material: tests, CI of knowledge-base itself, internal
  module structure.
- Keep the existing wording of correct paragraphs; change only what is wrong,
  missing or obsolete. Remove documentation of features the release removed.

### Landing page

`data/showcase.yml` holds the landing page as raw HTML. It presents the
**Knowledge Base** as the product, and the Docs Template as one of its features.
Keep the existing structure and CSS classes (`sc-*`), the `<!-- ── Navigation ── -->`
/ `<!-- ── /Navigation ── -->` markers around the `<nav>`, and relative links
(`docs/…/`). The navigation links point to the section entry pages of the guide.
In `full` mode, (re)write the hero, feature grid and calls to action so they
match the guide. In `incremental` mode, change the landing page only when a
headline feature was added or removed.

### Changelog

Add an entry at the top of `docs/kb/changelog.md` for the target release: the
release tag, its date, and a bullet list of user-facing changes since the
previous synced release, each linking to the page that documents it.

### Manifest

`kb-docs.json` `apps[0].pages` is written by the build; do not edit it. Keep
`name`, `description` and `tags` describing the Knowledge Base user guide.

### Feature map

Update `.kb-sync/features.yml`: add new features, fix `sources` and `page` where
they moved, remove features the release removed, and set `synced.tag` and
`synced.sha` to the target tag and its commit.

## 5. Verify

Run `python scripts/pack.py --headless` and make sure it succeeds without
warnings about missing pages or broken links. Do not commit `dist/`,
`./.kb-upstream` or generated `mkdocs-*.yml` files.

Do not edit anything under `.github/`, `theme/`, `scripts/` or
`package-lock.json`. If one of them needs a change, describe it in the pull
request body instead.

## 6. Report

**incremental / full**: create one pull request titled
`docs: document knowledge-base <target tag>`. The body must contain:

- the mode and the release range (`<synced.tag> → <target tag>`, or "initial" for
  the first full run)
- a table of features: added / updated / removed, and the page for each
- upstream disagreements found (prose vs code), with file paths
- changes needed outside your area that you did not make
- a `## Release Notes` section with bullet points of the user-visible changes to
  the guide

**audit**: make no file changes. Create one issue titled
`Docs drift against knowledge-base <target tag>` listing, per page, every
statement that is wrong, missing or obsolete, every feature not in the map, and
every upstream disagreement, each with the source file that proves it.

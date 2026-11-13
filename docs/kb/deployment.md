---
title: Deployment
order: 42
section: Run a Knowledge Base
---

# Deployment

Deployment is deliberately **not** part of the Knowledge Base repository. A private
**deployment repository** owns the production registry, the cloud account and the
schedule; the Knowledge Base is the build tool it calls. Normative source:
[DEPLOYMENT.md](https://github.com/AbsaOSS/knowledge-base/blob/v1.3.1/contract/DEPLOYMENT.md);
a copy-paste skeleton is in
[`examples/deployment-repo/`](https://github.com/AbsaOSS/knowledge-base/tree/v1.3.1/examples/deployment-repo).

| | Knowledge Base (public) | Deployment repo (private) |
|---|---|---|
| The build, publishing actions, contract | yes | — |
| Which docs, which versions (`apps.json`) | no (its own is a CI fixture) | yes |
| Cloud account, image registry, schedule | no | yes |

```
deployment-repo/
├─ apps.json
└─ .github/workflows/
   ├─ build.yml     # calls the reusable workflow
   └─ deploy.yml    # your cloud's deploy step
```

## The registry

Source-only entries, as in [Registry](registry.md):

```json
[
  { "repo": "AbsaOSS/my-service-docs", "version": "latest" },
  { "repo": "AbsaOSS/platform-docs",   "version": "v2.1.0" }
]
```

`latest` follows the docs repo; pin a tag for anything that must not move unreviewed.
A [strict build](building.md#strict-mode) rejects `prebuilt`, `localPath` and `optional`.
`iframe` entries are allowed.

## The reusable workflow

`AbsaOSS/knowledge-base/.github/workflows/build-image.yml@v1` builds the site and,
optionally, a Docker image.

```yaml
name: Build

on:
  push:
    branches: [main]
    paths: [apps.json]
  repository_dispatch:
    types: [kb-docs-published]
  schedule:
    - cron: '0 3 * * *'
  workflow_dispatch:

concurrency:
  group: kb-build
  cancel-in-progress: true

permissions:
  contents: read
  packages: write

jobs:
  build:
    uses: AbsaOSS/knowledge-base/.github/workflows/build-image.yml@v1
    with:
      kb-ref: v1.3.1
      registry: apps.json
      image-name: ghcr.io/your-org/knowledge-base
      image-tags: |
        {% raw %}${{ github.sha }}{% endraw %}
        latest
    secrets:
      docs-token: {% raw %}${{ secrets.DOCS_READ_TOKEN }}{% endraw %}
```

### Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `kb-ref` | no | the ref the workflow was called at | Ref of the Knowledge Base to build with. Pin a tag for reproducibility. |
| `registry` | no | `apps.json` | Registry file in the **calling** repository (`KB_REGISTRY`). |
| `headless` | no | `true` | Web-fragment output; standalone when `false`. |
| `strict` | no | `true` | Strict build. Leave on for a real deployment. |
| `image-name` | no | empty | Image to build and push. Empty means a dry run: `dist/` is uploaded as a workflow artifact and nothing is pushed. |
| `image-tags` | no | the run's SHA | Newline- or comma-separated tags. |
| `registry-host` | no | `ghcr.io` | Container registry to log in to. |
| `runs-on` | no | `ubuntu-latest` | A label, or a JSON array/object for several labels or a runner group. |
| `npm-registry` | no | empty | See [Private networks](private-networks.md). |
| `node-mirror` | no | empty | See [Private networks](private-networks.md). |

### Secrets

| Secret | Required | Description |
|---|---|---|
| `docs-token` | no | Token with `contents: read` on every registered docs repo. Falls back to `github.token`, which reads public repos only. |
| `registry-username`, `registry-password` | no | Container registry login (username defaults to the actor). |
| `npm-token`, `node-mirror-token`, `ca-certificates` | no | See [Private networks](private-networks.md). |

### Outputs

| Output | Description |
|---|---|
| `image` | The first pushed image reference, when one was pushed. |

## Reading the docs repos: a GitHub App

Create a GitHub App (for example `knowledge-base-builder`) installed on every registered
docs repository with **`contents: read`** only, and mint a short-lived installation token
per run to pass as `docs-token`. It is scoped to the repositories it is installed on,
expires in an hour, and belongs to the organisation rather than a person. Private docs
repos work because release assets are read through the API.

## Rebuilding when a docs repo publishes

Set `notify-repo` and `notify-token` on the [publish actions](actions.md#publish-docs).
A successful publish fires a `repository_dispatch` of type `kb-docs-published` carrying
`{ repo, tag, slugs }`. The token needs `contents: write` on the deployment repo only.
Treat the dispatch as an optimisation: the nightly schedule is the safety net.

## Rolling back

The image is immutable, so the fastest rollback is redeploying the previous tag with your
cloud's tooling. To roll back **content**, pin the offending entry in `apps.json` to its
previous release and rebuild. `kb-build.json` (uploaded as the `kb-build-provenance`
artifact and shown in the job summary) records what each build used; see
[Building](building.md#output).

## Checklist

- [ ] `apps.json` has source-only entries, no `prebuilt` / `localPath` / `optional`
- [ ] A GitHub App with `contents: read` is installed on every registered docs repo
- [ ] `build.yml` calls the reusable workflow with `kb-ref` pinned to a tag
- [ ] `strict` is left at its default
- [ ] Triggers: registry push, `repository_dispatch`, a schedule, manual
- [ ] `concurrency` collapses a burst of publishes into one build
- [ ] A dry-run check on PRs to the registry (`image-name` empty)

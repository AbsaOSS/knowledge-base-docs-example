---
title: GitHub Actions
order: 25
section: Publish Your Docs
---

# GitHub Actions

Three reusable composite actions live in `AbsaOSS/knowledge-base/actions/`. They share
one pinned dependency tree, so your repo needs no toolchain, `package.json` or lockfile
for them. They run on Node 20.

All three also take `npm-registry`, `npm-token`, `node-mirror` and `node-mirror-token`
for runners without public internet; see [Private networks](private-networks.md).

## publish-docs

Validates a built headless site against the [contract](rules.md), packs
`kb-docs.tar.gz`, and attaches it to a release (replacing an existing asset of that
name).

```yaml
- uses: AbsaOSS/knowledge-base/actions/publish-docs@v1
  with:
    manifest: kb-docs.json
    dist: dist
```

| Input | Required | Default | Description |
|---|---|---|---|
| `manifest` | no | `kb-docs.json` | Path to the manifest, relative to the workspace. |
| `dist` | no | `dist` | The built headless output. With one app, that app's directory; with several, a directory holding one subdirectory per slug. |
| `release-tag` | no | triggering release, else the latest | Release to attach to. |
| `github-token` | no | `{% raw %}${{ github.token }}{% endraw %}` | Needs `contents: write`. |
| `notify-repo` | no | empty | `owner/name` of a deployment repo to notify after publishing. Needs `notify-token`; skipped silently if either is unset. |
| `notify-token` | no | empty | Token with `contents: write` on `notify-repo` only. The default token cannot dispatch to another repository. |
| `npm-registry`, `npm-token`, `node-mirror`, `node-mirror-token` | no | empty | See [Private networks](private-networks.md). |

| Output | Description |
|---|---|
| `slugs` | Comma-separated slugs published. |
| `count` | Number of apps in the artifact. |
| `artifact` | Absolute path of the packed `kb-docs.tar.gz`. |
| `release-tag` | Tag of the release it was uploaded to. |

With `notify-repo` and `notify-token` set, a successful publish fires a
`repository_dispatch` of type `kb-docs-published` carrying `{ repo, tag, slugs }` at the
deployment repo, so it rebuilds without waiting for its schedule. A failed notify never
fails the publish. See [Deployment](deployment.md#rebuilding-when-a-docs-repo-publishes).

## check-docs

Runs the same checks on a pull request without packing or uploading anything. Findings
are annotated by rule ID and summarised on the run. Add it next to the publish workflow
with the same build step and `dist`.

```yaml
on: pull_request

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build -- --headless
      - uses: AbsaOSS/knowledge-base/actions/check-docs@v1
        with:
          manifest: kb-docs.json
          dist: dist
```

| Input | Required | Default | Description |
|---|---|---|---|
| `manifest` | no | `kb-docs.json` | Path to the manifest. |
| `dist` | no | `dist` | The built headless output, as for `publish-docs`. |
| `strict` | no | `false` | `"true"` also fails on warnings. Errors always fail. |
| `npm-registry`, `npm-token`, `node-mirror`, `node-mirror-token` | no | empty | See [Private networks](private-networks.md). |

| Output | Description |
|---|---|
| `errors` | Number of error findings. |
| `warnings` | Number of warning findings. |

## publish-single-page-docs

Renders Markdown into headless HTML and publishes it. See [Single-page docs](single-page.md).

| Input | Required | Default | Description |
|---|---|---|---|
| `docs` | yes | — | YAML or JSON list of doc definitions (`md`, `title`, `description`, `slug`, optional `icon`, `tags`). |
| `release-tag` | no | triggering release, else the latest | Release to attach to. |
| `github-token` | no | `{% raw %}${{ github.token }}{% endraw %}` | Needs `contents: write`. |
| `npm-registry`, `npm-token`, `node-mirror`, `node-mirror-token` | no | empty | See [Private networks](private-networks.md). |

Outputs: `slugs`, `count`, `artifact`, `release-tag`, as for `publish-docs`.

## Versioning

Pin to the floating major tag (`@v1`), not a branch. Pushing a `vMAJOR.MINOR.PATCH`
tag moves the major tag to it. A breaking contract change is a new major (`@v2`) with a
`kbVersion` bump, so repos pinned to `@v1` keep publishing against the contract they
were written for.

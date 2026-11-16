---
title: Private networks
order: 44
section: Run a Knowledge Base
---

# Private networks

If your runners have no route to `registry.npmjs.org` (every package comes from an
internal Artifactory, say), pass a registry to the same step. This applies to the
[three publish/check actions](actions.md), to the
[reusable build workflow](deployment.md#the-reusable-workflow), and to the Docker image build.

## Inputs

The actions take these four inputs; `build-image.yml` takes the same as
`npm-registry`/`node-mirror` inputs and `npm-token`/`node-mirror-token` secrets.

| Input | Description |
|---|---|
| `npm-registry` | npm registry to install the tool's own dependencies from. Must be an `http(s)` URL with no whitespace. Empty means whatever npm resolves on the runner. |
| `npm-token` | Auth token for `npm-registry`. Omit for anonymous reads. |
| `node-mirror` | Mirror of `https://nodejs.org` for `setup-node`, when the runner reaches neither nodejs.org nor the github.com release assets. Not needed if the image carries Node in its tool cache (Node 20 for the actions, Node 24 for the build workflow). |
| `node-mirror-token` | `Authorization` header value for `node-mirror`. |

```yaml
- uses: AbsaOSS/knowledge-base/actions/publish-docs@v1
  with:
    npm-registry: https://artifactory.example.com/artifactory/api/npm/npm-remote/
    npm-token: {% raw %}${{ secrets.ARTIFACTORY_TOKEN }}{% endraw %}   # omit for anonymous reads
```

The lockfile names no registry, only versions and integrity hashes, so one action ref
installs on GitHub-hosted and internal runners alike. The setting applies to that install
only and the token is never written to disk. A runner whose own `~/.npmrc` already names
the mirror needs none of these inputs.

## A deployment on private runners

```yaml
  build:
    uses: AbsaOSS/knowledge-base/.github/workflows/build-image.yml@v1
    with:
      kb-ref: v1.3.1
      registry: apps.json
      image-name: artifactory.example.com/docker-local/knowledge-base
      registry-host: artifactory.example.com
      runs-on: '["self-hosted", "linux"]'
      npm-registry: https://artifactory.example.com/artifactory/api/npm/npm-remote/
      node-mirror: https://artifactory.example.com/artifactory/nodejs-remote
    secrets:
      docs-token: {% raw %}${{ secrets.DOCS_READ_TOKEN }}{% endraw %}
      npm-token: {% raw %}${{ secrets.ARTIFACTORY_TOKEN }}{% endraw %}
      registry-username: {% raw %}${{ secrets.ARTIFACTORY_USER }}{% endraw %}
      registry-password: {% raw %}${{ secrets.ARTIFACTORY_TOKEN }}{% endraw %}
      ca-certificates: {% raw %}${{ secrets.CORP_CA_PEM }}{% endraw %}
```

## CA certificates

Behind a TLS-intercepting proxy the image build's `apk upgrade` fails with
`TLS: server certificate not trusted`, because the base image trusts public CAs only.

- Through the workflow, pass the PEM as the `ca-certificates` secret. It is written to
  `trusted_certs/` before `docker build`.
- Building yourself, drop `*.pem` / `*.crt` files into `trusted_certs/`, or use
  `docker build --build-arg TRUSTED_SSL_CERTS=./my-certs .`. Every file is appended to the
  system CA bundle before `apk` runs; the certificates stay in the image.

## What no input can cover

- `docker build` pulls the nginx base image from Docker Hub by digest. Configure a
  `registry-mirrors` entry in the runner's `/etc/docker/daemon.json`; the digest verifies
  the mirror served the same image.
- `setup-node`'s npm cache uses GitHub's cache service, and the App token comes from
  `api.github.com`. Both must be reachable from a self-hosted runner.

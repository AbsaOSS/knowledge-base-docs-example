---
title: Docker and nginx
order: 43
section: Run a Knowledge Base
---

# Docker and nginx

The runtime image serves a prebuilt `dist/` with nginx. Build `dist/` first, then the
image:

```bash
npm run build:headless
docker build -t knowledge-base .
docker run -p 8080:8080 knowledge-base
```

The `Dockerfile` copies `dist/` into the image and fails if `dist/index.html` or
`dist/style.css` is missing.

## Image

- Base: `nginxinc/nginx-unprivileged` (Alpine), pinned by digest. It runs as UID 101 and
  listens on **port 8080**.
- `apk upgrade` runs at build time to pick up Alpine security fixes.
- Health check: `GET /healthz` returns `200 ok`, polled every 30 s.

For building behind a TLS-intercepting proxy, see [Private networks](private-networks.md#ca-certificates).

## Routes

| Path | Behaviour |
|---|---|
| `/healthz` | `200 ok`, no access log. |
| `/knowledge-base/*` | The prefix is stripped and files resolve from the `dist/` root; directories serve `index.html`. |
| `/__wf/knowledge-base/*` | The fragment asset prefix; stripped the same way. Used when [embedded](embedding.md). |
| `/knowledge-base` | Internal rewrite to `/knowledge-base/` (no redirect, which would leak the internal address and cause mixed content behind HTTPS). |
| `OPTIONS` | `204`. |

## Caching

| Resource | `Cache-Control` |
|---|---|
| Astro's hashed `_astro/` output and content-addressed `_kb-inline/<16 hex>.js` scripts | `public, max-age=31536000, immutable, no-transform` |
| Everything else: HTML, `style.css`, sub-app assets | `no-cache, no-transform` (revalidated by ETag) |

`no-transform` stops an intermediate gateway re-encoding the body. Gzip is on for CSS,
JavaScript, JSON, SVG and woff2 (not HTML).

## Headers

Every response carries:

| Header | Value |
|---|---|
| `Access-Control-Allow-Origin` | `*` |
| `Access-Control-Allow-Methods` | `GET, OPTIONS` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `SAMEORIGIN` (`DENY` would break the web-fragment iframe) |
| `Referrer-Policy` | `strict-origin` |
| `Content-Security-Policy` | see below |

```text
default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';
img-src 'self' data: https:; font-src 'self' data:; connect-src 'self';
frame-src 'self' https: blob:; worker-src 'self' blob:; frame-ancestors 'self';
base-uri 'none'; form-action 'self'; object-src 'none'
```

`script-src 'self'` is why docs must ship [scripts as files](packaged.md#scripts-as-files).
`img-src` allows `https:` images; scripts, styles and fonts from other origins are blocked
([KB-CSP-001](rules.md#css-theme-csp-javascript)). `frame-src` allows `https:` for
[iframe entries](registry.md#iframe-entries).

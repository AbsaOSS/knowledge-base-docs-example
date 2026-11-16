---
title: Web fragment embedding
order: 60
section: Embed in a Host App
---

# Embedding as a web fragment

The Knowledge Base can run as a [web fragment](https://web-fragments.dev) inside any host
app that uses a web-fragments gateway (Express/Node, Cloudflare, Angular SSR…). The
gateway proxies `/knowledge-base/*` onto the host's single origin and reframes the
markup into a shadow root, with no full page reload between pages.

## 1. Build and serve the fragment

Build headless output (`npm run build:headless`, see [Building](building.md)) and serve
`dist/` with the same rewrites as the [nginx image](docker-nginx.md): `/knowledge-base/*`
and `/__wf/knowledge-base/*` both resolve from the `dist/` root.

## 2. Register it on the gateway

```js
import { FragmentGateway } from 'web-fragments/gateway';
import { getNodeMiddleware } from 'web-fragments/gateway/node';

const gateway = new FragmentGateway();
gateway.registerFragment({
  fragmentId: 'knowledge-base',
  endpoint: 'http://localhost:3000',          // the fragment server
  piercing: false,                            // or true (SSR piercing)
  routePatterns: [
    '/knowledge-base/:_*',                    // landing, app pages, assets
    '/__wf/knowledge-base/:_*',               // fragment asset prefix
  ],
});
app.use(getNodeMiddleware(gateway));          // before host static/catch-all routes
```

## 3. Add it to a host page

```html
<script type="importmap">{ "imports": { "web-fragments": "/_wf/elements.js" } }</script>
<web-fragment fragment-id="knowledge-base" src="/knowledge-base/"></web-fragment>
<script type="module">
  import { initializeWebFragments } from 'web-fragments';
  initializeWebFragments();
</script>
```

`initializeWebFragments()` must run before anything renders a `<web-fragment>`. With
piercing on, an earlier element fails with `portalHost is not a function` and falls
back to client rendering.

## Host router and fragment history

`src` on `<web-fragment>` decides how the fragment's history relates to the host's.

| | `src` set — **unbound** | no `src` — **bound** |
|---|---|---|
| Fragment history | private stack inside the reframed iframe | the host's `window.history` |
| Address bar | never moves; the host router hears nothing | moves to `/knowledge-base/…` per page; the host router gets a `popstate` |
| Deep links, back/forward | none | work |
| Host route needed | the one route the element sits on | a wildcard covering every fragment page: `/knowledge-base/**` |

**Unbound** is the safe default when the host router must own the URL. `src` is read once
when the element connects; re-create the element to show a different page.

**Bound** gives fragment pages real URLs. The host route config must cover the whole
prefix, otherwise the first click lands on the host's fallback route and destroys the
fragment. In Angular:

```ts
// app.routes.ts
{ path: 'knowledge-base', children: [{ path: '**', component: KnowledgeBasePage }] }

// main.ts — before bootstrapApplication()
import { initializeWebFragments } from 'web-fragments';
initializeWebFragments();
```

Guards and resolvers on that route run on every fragment page. Document requests for
`/knowledge-base/…` reach the host, so Angular SSR must render the shell for them; the
wildcard route does that. An Angular host also needs `"outputMode": "server"` and
`"externalDependencies": ["web-fragments/gateway", "web-fragments/gateway/node", "htmlrewriter"]`
in its build target.

## What to know when you publish docs

Pages are re-hosted inside the host document, so [contract rules](rules.md) such as
KB-HTML-008 (links to non-HTML files) and KB-JS-001 (page-relative `fetch()` URLs) exist
specifically for embedded use. Navigation between pages is by Astro's client router, with
view transitions.

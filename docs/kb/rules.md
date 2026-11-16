---
title: Contract rules and the checker
order: 24
section: Publish Your Docs
---

# Contract rules and the checker

Every requirement a published site is checked against has an ID. A finding names one
ID. The normative list is
[RULES.md](https://github.com/AbsaOSS/knowledge-base/blob/v1.3.1/contract/RULES.md).

**Severity:**

- **error** — the publish stops, with every error listed at once.
- **warning** — annotated on the workflow run; the publish goes ahead. The Knowledge Base
  repairs it when re-hosting the page, or it only hurts that page. Fix it anyway.

New rules start as warnings. A warning becomes an error only in a new major version of
the actions, so a repo pinned to `@v1` never starts failing on an unseen rule.

## Running the checks

- **On release**: the `publish-docs` action runs them before packing.
- **On a pull request**: the `check-docs` action runs the same checks without releasing.
  See [Actions](actions.md#check-docs).
- **Locally**:

  ```bash
  git clone --depth 1 https://github.com/AbsaOSS/knowledge-base.git /tmp/knowledge-base
  npm ci --omit=dev --prefix /tmp/knowledge-base/actions
  node /tmp/knowledge-base/actions/lib/check-cli.js --manifest kb-docs.json --dist dist
  ```

| Flag | Meaning |
|---|---|
| `--manifest <path>` | Manifest to check. Default `kb-docs.json`. |
| `--dist <dir>` | Built headless output. Default `dist`. |
| `--json` | Print findings as a JSON array (`id`, `severity`, `where`, `message`). |
| `--strict` | Exit non-zero on warnings as well as errors. |

The Knowledge Base build runs the same checks on every artifact it installs and logs the
findings; a strict (production) build refuses an artifact with an error finding.

## Manifest and artifact

| ID | Severity | Rule |
|---|---|---|
| KB-MAN-001 | error | `kb-docs.json` exists and satisfies the schema |
| KB-ART-001 | error | The entry point exists in the built output |
| KB-ART-002 | error | Every `pages` entry exists in the built output |
| KB-ART-003 | error | Each app contains HTML |
| KB-ART-004 | warning | The artifact is at most 20 MB |
| KB-ART-005 | error | The artifact is at most 100 MB |

For KB-ART-001, the usual cause is a `dist` input pointing at the wrong directory — with
several apps, `dist` must hold one subdirectory per slug.

## HTML

| ID | Severity | Rule | Fix |
|---|---|---|---|
| KB-HTML-001 | error | Every page is marked headless | `data-kb-headless="true"` on `<html>`. The pre-v1 `data-mp-headless` is reported by name: republish with a current action. |
| KB-HTML-002 | error | No `<base>` element | Remove it. |
| KB-HTML-003 | error | No root-relative URLs in `href`, `src`, `action`, `formaction`, `poster` | Use relative paths (`guide/`, `../img/x.png`). `/favicon…` and `//host/…` are not checked. |
| KB-HTML-004 | warning | No inline `<script>` blocks | Ship scripts as files. JSON data blocks (`application/ld+json`) are not reported. |
| KB-HTML-005 | warning | No inline event handler attributes | Attach listeners from a script file. They are stripped on re-hosting. |
| KB-HTML-006 | warning | No `javascript:` URLs | Use a `<button>` with a listener from a script file. |
| KB-HTML-007 | warning | No site-level `<header>` directly inside `<body>` | Leave out the site bar. A `<header>` inside an article or section is fine. |
| KB-HTML-008 | warning | No links to non-HTML files in the app | When embedded, a document request for a PDF or ZIP reaches the host app instead. Link to an HTML page, or host downloads elsewhere. Other origins are not reported. |

## CSS, theme, CSP, JavaScript

| ID | Severity | Rule | Fix |
|---|---|---|---|
| KB-CSS-001 | warning | No `!important` declarations | Raise specificity. Important declarations invert cascade-layer order and beat the Knowledge Base's own rules. |
| KB-THEME-001 | warning | No dark mode | Drop the theme bootstrap and the `dark` class; they are deleted on re-hosting. |
| KB-CSP-001 | warning | No scripts, stylesheets or fonts from another origin | Ship them with the site. The policy is `script-src 'self'`, `style-src 'self' 'unsafe-inline'`, `font-src 'self' data:`. Images from `https:` are allowed. |
| KB-JS-001 | warning | No fetches of page-relative URLs | Resolve against the script: `new URL('data.json', import.meta.url)`, or `document.currentScript.src`. A literal relative URL in `fetch()` or `XMLHttpRequest.open()` is reported (textual check). |

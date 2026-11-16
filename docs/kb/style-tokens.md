---
title: Style tokens
order: 26
section: Publish Your Docs
---

# Style tokens

Packaged docs must look consistent with the Knowledge Base. Normative source:
[STYLE_GUIDE.md](https://github.com/AbsaOSS/knowledge-base/blob/v1.3.1/contract/STYLE_GUIDE.md).
(Single-page docs get their styling from the action.)

## Required tokens

Your CSS must define, or import, at least:

```css
--color-kb-500, --color-kb-600
--bg-page, --bg-card, --bg-subtle, --bg-strong
--border, --border-subtle
--text-heading, --text-body, --text-muted
```

Copy the `@theme` block and `:root` variables from `src/styles/knowledge-base.css` in the
Knowledge Base repository. There is deliberately no `.dark` set.

## Palette

Use the brand tokens, never raw hex values.

| Token | Hex | Usage |
|---|---|---|
| `--color-kb-500` | `#af144b` | Primary brand, links, active states, focus rings |
| `--color-kb-600` | `#93103f` | Hover for primary elements |
| `--color-kb-400` | `#d4547a` | Accents |
| `--color-kb-100` | `#f0d0da` | Subtle tint backgrounds |
| `--color-kb-50` | `#f8eaee` | Very light tint |
| `--color-kb-25` | `#fdf8f9` | Page background |
| `--color-kb-950` | `#1b0e12` | Heading text |

## Typography and shape

| Role | Font | Token |
|---|---|---|
| Body / UI | Inter, Noto Sans | `--font-sans` |
| Code | SF Mono, Fira Code | `--font-mono` |

| Token | Value |
|---|---|
| `--radius-sm` | `6px` |
| `--radius-md` | `12px` |
| `--radius-lg` | `16px` |
| `--radius-xl` | `20px` |

The Knowledge Base self-hosts Inter. Do not load fonts from another origin: it is
blocked by the CSP (KB-CSP-001 in [Contract rules](rules.md)); bundle the font with your site.

## Light only

There is no dark mode, theme toggle or persisted preference. The build strips a
`localStorage` theme script and a `dark` class from `<body>`. An app may keep `.dark`
styles for its standalone deployment; they never activate inside the Knowledge Base.

## Layout

- Fixed left sidebar, 64px wide (`w-64`), `id="sidebar"`, `top: 0`, with `<nav aria-label="Documentation">`.
- Content in `id="content"` or `<main>`, left margin `ml-64` on desktop, prose at most `max-w-3xl`.
- Interactive elements have accessible names; focus rings use `--color-kb-500`; images have `alt`.

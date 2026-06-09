---
title: Adding Pages
order: 3
---

# Adding Pages

## Adding a Markdown page

**Step 1** — Create a `.md` file in the `docs/` folder with frontmatter:

```
docs/
├── index.md
├── customising.md
└── my-new-page.md   ← new file
```

```yaml
---
title: My New Page
order: 4
---

# My New Page

Your content here.
```

**Step 2** — Run `npm run dev` to preview. Navigation is auto-generated from frontmatter — no config editing needed.

You can also create pages through the CMS at `/admin/`.

## Adding a standalone HTML page

Standalone HTML pages (like `showcase.html`) are copied into `dist/` by the build script — they live alongside the MkDocs output.

**Step 1** — Create your HTML file at the repo root:

```
knowledge-base-docs-example/
├── showcase.html
└── calculator.html   ← new standalone page
```

**Step 2** — In `scripts/pack.py`, add a copy line in the section that handles showcase assets:

```bash
cp calculator.html dist/calculator.html
```

**Step 3** — Link to it from any Markdown page using a root-relative path:

```markdown
[Open the calculator](../calculator.html)
```

Or from another HTML page:

```html
<a href="calculator.html">Open the calculator</a>
```

## Linking between docs and the showcase

From Markdown, link to the showcase landing page:

```markdown
[Back to overview](../index.html)
```

From the showcase HTML, link into the docs:

```html
<a href="docs/index.html">Read the docs</a>
```

## Cross-linking between Markdown pages

Use relative paths without the `.md` extension in links:

```markdown
See [Customising](customising.md) for config options.
```

MkDocs resolves these to the correct `.html` paths in the built output.

---

> **Need more?** The full user guide covering tool setup and knowledge base registration is available in the knowledge base documentation.

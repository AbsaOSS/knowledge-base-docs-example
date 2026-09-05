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

Standalone HTML pages are copied into `dist/` by the build script — they live alongside the MkDocs output, next to the showcase landing page.

**Step 1** — Create your HTML file at the repo root:

```
knowledge-base-docs-example/
├── showcase.css
└── calculator.html   ← new standalone page
```

Give it `data-kb-headless="true"` on `<html>`, no `<base>`, and only relative
`href`/`src` paths — the publish action checks every HTML file in `dist/`.

**Step 2** — In `scripts/pack.py`, copy it next to the showcase in `render_showcase()`:

```python
shutil.copy2("calculator.html", "dist/calculator.html")
```

**Step 3** — Link to it from any Markdown page using a relative path:

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

## Embedding SharePoint videos

MkDocs renders Markdown, not MDX — but reusable components are available through
[mkdocs-macros](https://mkdocs-macros-plugin.readthedocs.io/). Call the
`sharepoint_video` macro from any `.md` page to drop in a responsive video:

```markdown
{% raw %}{{ sharepoint_video('https://absa.sharepoint.com/.../video.mp4', title='Onboarding demo') }}{% endraw %}
```

This renders a responsive 16:9 iframe that scales with the page. Arguments:

| Argument | Required | Notes |
|---|---|---|
| `url` | Yes | SharePoint share/embed URL. In SharePoint use **Share → Embed** and copy the `src`; a plain share link usually works too (append `&embed=true` if the player does not load). |
| `title` | No | Accessible label for screen readers. |
| `ratio` | No | Aspect-ratio padding. `"56.25%"` = 16:9 (default), `"75%"` = 4:3. |

Macros are defined in `main.py` at the repo root — add your own there to build
more reusable components.

## Adding images

Upload images through the CMS at `/admin/`, or drop files into
`docs/assets/images/` and reference them with a path relative to your page:

```markdown
![Architecture diagram](assets/images/diagram.png)
```

MkDocs rewrites the path to the correct URL at build time, so it works both
locally and when the site is served under a subpath.

## Cross-linking between Markdown pages

Use relative paths without the `.md` extension in links:

```markdown
See [Customising](customising.md) for config options.
```

MkDocs resolves these to the correct `.html` paths in the built output.

---

> **Need more?** The full user guide covering tool setup and knowledge base registration is available in the knowledge base documentation.

---
title: Customising
order: 2
---

# Customising the Template

Two files control everything a team needs to customise. The rest — theme, build script, CSS, CI pipeline — works out of the box.

## `marketplace.json`

Tells the Knowledge Base how to catalogue your docs.

```json
{
  "marketplaceVersion": "1",
  "name": "My Team Docs",
  "slug": "my-team",
  "description": "Short description shown on the knowledge base card.",
  "icon": "book-open",
  "tags": ["my-team", "guide"],
  "entryPoint": "index.html"
}
```

| Field | Required | Notes |
|---|---|---|
| `slug` | Yes | Lowercase letters, numbers, hyphens — becomes the URL path |
| `name` | Yes | Display name in the knowledge base catalogue |
| `description` | Yes | One-line summary on the catalogue card |
| `icon` | No | Icon name from the knowledge base icon set |
| `tags` | No | Array of filter labels |
| `entryPoint` | Yes | Always `"index.html"` |

The build script automatically adds a `pages` array to `dist/marketplace.json` at build time — you never edit it by hand. Each doc page is discovered from the `docs/` folder and its `title` / `order` / `section` frontmatter. The knowledge base uses this to generate static routes without crawling the filesystem.

To control the order of a page, set `order` in its frontmatter:

```yaml
---
title: My Page
order: 4
---
```

To place a page under a sidebar section, add `section`:

```yaml
---
title: API Reference
order: 5
section: Reference
---
```

Navigation is **auto-generated** from frontmatter at build time — no manual `nav:` editing required.

## `mkdocs.yml`

Controls the site name and theme settings. Navigation is generated automatically.

```yaml
site_name: My Team Docs          # shown in the top nav bar
site_description: One line.
docs_dir: docs
site_dir: dist/docs              # leave as-is

theme:
  name: null
  custom_dir: theme              # leave as-is

# nav is auto-generated from frontmatter (title, order, section) by pack.py
```

## Showcase landing page

The landing page at `dist/index.html` is rendered from `data/showcase.yml` through a Jinja2 template (`showcase.html`). Edit the YAML file to change headings, feature cards, steps, and CTA buttons — or use the CMS at `/admin/` for a visual editor.

Styles live in `showcase.css`. Design tokens are at the top of the file.

> **Full user guide:** For VS Code setup and the knowledge base registration process, see the complete guide in the knowledge base documentation.

Next: [Adding Pages](adding-pages.md)

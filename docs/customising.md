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

The build script automatically adds a `pages` array to `dist/marketplace.json` at build time — you never edit it by hand. Each doc page is read from `mkdocs.yml` nav order and the `title` / `order` frontmatter in each Markdown file. The knowledge base uses this to generate static routes without crawling the filesystem.

To control the order of a page, set `order` in its frontmatter:

```yaml
---
title: My Page
order: 4
---
```

To place a page under a sidebar section, add it to a section group in `mkdocs.yml`:

```yaml
nav:
  - Overview: index.md
  - Reference:
    - API: reference/api.md
```

## `mkdocs.yml`

Controls the site name and sidebar navigation.

```yaml
site_name: My Team Docs          # shown in the top nav bar
site_description: One line.
docs_dir: docs
site_dir: dist/docs              # leave as-is

theme:
  name: null
  custom_dir: theme              # leave as-is

nav:
  - Overview: index.md           # sidebar order = list order
  - Getting Started: getting-started.md
  - Reference: reference.md
```

To add a page: create the `.md` file in `docs/`, then add it to `nav:`.

To group pages into sections:

```yaml
nav:
  - Overview: index.md
  - User Guide:
    - Getting Started: guide/getting-started.md
    - Configuration: guide/configuration.md
  - Reference:
    - API: reference/api.md
```

## `showcase.html`

The landing page at `dist/index.html`. Edit it to describe your product or service. Styles are shared with the docs bundle — design tokens are at the top of `theme/style.css`. You do not need to touch any CSS files.

> **Full user guide:** For VS Code setup and the knowledge base registration process, see the complete guide in the knowledge base documentation.

Next: [Adding Pages](adding-pages.md)

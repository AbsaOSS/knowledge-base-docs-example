---
title: Customising
order: 2
---
# Customising the Template

Two files control everything a team needs to customise. The rest — theme, build script, CSS, CI pipeline — works out of the box.

## `kb-docs.json`

Tells the Knowledge Base how to catalogue your docs. It is the version 1 manifest of the knowledge base contract: a list of apps, of which this template publishes exactly one.

```json
{
  "kbVersion": "1",
  "apps": [
    {
      "slug": "my-team",
      "name": "My Team Docs",
      "description": "Short description shown on the knowledge base card.",
      "icon": "book-open",
      "tags": ["my-team", "guide"],
      "entryPoint": "index.html"
    }
  ]
}
```

| Field         | Required | Notes                                                                                   |
| ------------- | -------- | --------------------------------------------------------------------------------------- |
| `kbVersion`   | Yes      | Always `"1"` — leave as-is                                                              |
| `slug`        | Yes      | Lowercase letters, numbers, hyphens — becomes the URL path. Unique across the whole KB  |
| `name`        | Yes      | Display name in the knowledge base catalogue                                            |
| `description` | Yes      | One-line summary on the catalogue card (10–280 characters)                              |
| `icon`        | No       | Icon name from the knowledge base icon set                                              |
| `tags`        | No       | Up to five filter labels                                                                |
| `entryPoint`  | No       | Always `"index.html"`                                                                   |

The build script automatically writes a `pages` array into the app entry at build time — you never edit it by hand. Each doc page is discovered from the `docs/` folder and its `title` / `order` / `section` frontmatter. The knowledge base uses this to generate static routes without crawling the filesystem. The full field reference is on the [Publishing](publishing.md) page.

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

The landing page at `dist/index.html` is the raw HTML stored under `content:` in `data/showcase.yml`, wrapped into a full page by the build script. Edit that HTML to change headings, feature cards, steps, and CTA buttons — or use the CMS at `/admin/` for a live-preview editor. Keep the `<!-- ── Navigation ── -->` … `<!-- ── /Navigation ── -->` markers around the `<nav>`: the headless build removes exactly that block.

Styles live in `showcase.css`. Design tokens are at the top of the file.

> **Full user guide:** For the VS Code setup and the knowledge base registration process, see the complete guide in the knowledge base documentation.

Next: [Adding Pages](adding-pages.md)

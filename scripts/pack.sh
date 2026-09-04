#!/usr/bin/env bash
#
# Copyright 2026 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# pack.sh — build the docs site for the Knowledge Base (bash alternative to pack.py).
#
# Usage:
#   bash scripts/pack.sh            # standalone build → dist/
#   bash scripts/pack.sh --headless # headless build → dist/ (what the release publishes)
#   bash scripts/pack.sh --pack     # headless build + local kb-docs.tar.gz for inspection
#
# Every build refreshes apps[0].pages in kb-docs.json from docs/ frontmatter.
# Packing and publishing is the job of AbsaOSS/knowledge-base/actions/publish-docs
# (see .github/workflows/pack.yml); --pack mirrors its artifact layout so the
# result can be inspected without cutting a release.
#
# Prerequisites: pip install -r requirements.txt
#               Set SKIP_PIP_INSTALL=1 to bypass (e.g. managed environments where packages are pre-installed)

set -euo pipefail

MANIFEST=kb-docs.json
ASSET_NAME=kb-docs.tar.gz
HEADLESS_MARKER='data-kb-headless="true"'

# ── Detect Python binary ─────────────────────────────────────────────────────
if command -v python3 &>/dev/null; then
  PYTHON=python3
elif command -v python &>/dev/null; then
  PYTHON=python
else
  echo "❌ No python3 or python found in PATH"
  exit 1
fi

# ── Build-time cleanup ────────────────────────────────────────────────────────
# mkdocs-build.yml and mkdocs-headless-build.yml are generated during the build
# and must not be committed or left behind after the script exits.
_cleanup() {
  rm -f mkdocs-build.yml mkdocs-headless-build.yml
}
trap _cleanup EXIT

# ── Merge mkdocs.yml into build-time configs ──────────────────────────────────
# The generated configs are used for the actual mkdocs build so mkdocs.yml stays
# clean and uncommitted.
generate_build_configs() {
  $PYTHON - <<'PY'
import re, yaml, pathlib

def parse_frontmatter(md_path):
    text = pathlib.Path(md_path).read_text(encoding='utf-8')
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            kv = line.split(':', 1)
            if len(kv) == 2:
                k, v = kv[0].strip(), kv[1].strip()
                meta[k] = int(v) if v.isdigit() else v
    return meta

def auto_generate_nav(docs_dir='docs'):
    docs_path = pathlib.Path(docs_dir)
    pages = []
    for md_file in docs_path.rglob('*.md'):
        rel = md_file.relative_to(docs_path).as_posix()
        fm = parse_frontmatter(str(md_file))
        pages.append({
            'file': rel,
            'title': fm.get('title', md_file.stem.replace('-', ' ').title()),
            'order': fm.get('order', 999),
            'section': fm.get('section'),
        })
    pages.sort(key=lambda p: p['order'])

    top_level = []
    sections = {}
    section_min_order = {}
    for page in pages:
        entry = {page['title']: page['file']}
        sect = page['section']
        if sect:
            sections.setdefault(sect, []).append(entry)
            section_min_order[sect] = min(section_min_order.get(sect, 999), page['order'])
        else:
            top_level.append(entry)

    nav = list(top_level)
    for sect_name in sorted(sections, key=lambda s: section_min_order[s]):
        nav.append({sect_name: sections[sect_name]})
    return nav

cfg = yaml.safe_load(pathlib.Path('mkdocs.yml').read_text(encoding='utf-8'))
nav = auto_generate_nav(cfg.get('docs_dir', 'docs'))
cfg['nav'] = nav
print(f'  Auto-generated nav with {len(nav)} top-level entr(y/ies)')

pathlib.Path('mkdocs-build.yml').write_text(yaml.dump(cfg, default_flow_style=False, allow_unicode=True), encoding='utf-8')
PY

  # Headless variant inherits the merged base config and sets headless mode
  printf 'INHERIT: mkdocs-build.yml\n\nextra:\n  headless: true\n' > mkdocs-headless-build.yml
}

# ── Pages manifest → kb-docs.json ─────────────────────────────────────────────
# Writes the computed `pages` list into apps[0] of kb-docs.json, in place.
# kb-docs.json is the file the publish action reads, so the pages live there
# rather than in dist/. Only apps[0].pages is touched.
update_manifest_pages() {
  $PYTHON - <<'PY'
import json, pathlib, re, sys, yaml

MANIFEST = 'kb-docs.json'

def parse_frontmatter(md_path):
    text = pathlib.Path(md_path).read_text(encoding='utf-8')
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            kv = line.split(':', 1)
            if len(kv) == 2:
                k, v = kv[0].strip(), kv[1].strip()
                meta[k] = int(v) if v.isdigit() else v
    return meta

def output_path(md_rel):
    rel = pathlib.Path(md_rel).with_suffix('').as_posix()
    if rel == 'index':
        return 'docs/index.html'
    if rel.endswith('/index'):
        rel = rel[:-len('/index')]
    return f'docs/{rel}/index.html'

cfg = yaml.safe_load(pathlib.Path('mkdocs-build.yml').read_text(encoding='utf-8'))
nav = cfg.get('nav', [])

pages = []
order_counter = 1

def add_entries(items, section=None):
    global order_counter
    for item in items:
        if isinstance(item, dict):
            for label, value in item.items():
                if isinstance(value, str):  # leaf page
                    fm = parse_frontmatter(f'docs/{value}')
                    entry = {
                        'title': fm.get('title', label),
                        'path': output_path(value),
                        'order': fm.get('order', order_counter),
                    }
                    if section:
                        entry['section'] = section
                    elif fm.get('section'):
                        entry['section'] = fm['section']
                    pages.append(entry)
                    order_counter += 1
                elif isinstance(value, list):  # section group
                    add_entries(value, section=label)

add_entries(nav)

path = pathlib.Path(MANIFEST)
if not path.exists():
    sys.exit(f'❌ {MANIFEST} missing — see docs/publishing.md for its shape')
manifest = json.loads(path.read_text(encoding='utf-8'))
apps = manifest.get('apps')
if manifest.get('kbVersion') != '1' or not isinstance(apps, list) or len(apps) != 1:
    sys.exit(f'❌ {MANIFEST} must have "kbVersion": "1" and exactly one entry in "apps"')
apps[0]['pages'] = pages
path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'  {len(pages)} page(s) written to {MANIFEST} (apps[0].pages)')
PY
}

if [ "${SKIP_PIP_INSTALL:-0}" != "1" ]; then
  echo "▶ Installing Python dependencies..."
  $PYTHON -m pip install -r requirements.txt -q --break-system-packages
fi

HEADLESS=false
PACK=false
for arg in "$@"; do
  case "$arg" in
    --headless) HEADLESS=true ;;
    --pack) PACK=true; HEADLESS=true ;;   # only a headless build is a valid artifact
    *) echo "Unknown argument: $arg"; exit 1 ;;
  esac
done

echo "▶ Cleaning dist/..."
rm -rf dist/

echo "▶ Generating build configs..."
generate_build_configs

if [ "$HEADLESS" = true ]; then
  echo "▶ Building docs (headless)..."
  $PYTHON -m mkdocs build -f mkdocs-headless-build.yml
else
  echo "▶ Building docs..."
  $PYTHON -m mkdocs build -f mkdocs-build.yml
fi

if [ ! -f dist/docs/index.html ]; then
  echo "❌ dist/docs/index.html missing — build failed"
  exit 1
fi

if [ "$HEADLESS" = true ]; then
  echo "▶ Copying showcase (without nav) as entry point..."
  $PYTHON - <<'PY'
import re, pathlib
html = pathlib.Path('showcase.html').read_text(encoding='utf-8')
html = re.sub(r'<!-- ── Navigation ── -->\s*<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL)
# The knowledge base verifies every HTML file carries the headless marker on <html>.
html = re.sub(r'<html\b', '<html data-kb-headless="true"', html, count=1)
pathlib.Path('dist/index.html').write_text(html, encoding='utf-8')
PY
else
  echo "▶ Copying showcase as entry point..."
  cp showcase.html dist/index.html
fi
[ -f showcase.css ] && cp showcase.css dist/showcase.css

echo "▶ Updating $MANIFEST pages manifest..."
update_manifest_pages

if [ "$PACK" = true ]; then
  echo "▶ Packing $ASSET_NAME (local preview of the publish action)..."
  SLUG=$($PYTHON -c "import json; print(json.load(open('$MANIFEST', encoding='utf-8'))['apps'][0]['slug'])")

  missing=$(grep -rL --include='*.html' "$HEADLESS_MARKER" dist || true)
  if [ -n "$missing" ]; then
    echo "❌ HTML without $HEADLESS_MARKER on <html>:"
    echo "$missing" | sed 's/^/   • /'
    exit 1
  fi

  # Same layout and deterministic metadata as actions/publish-docs:
  # kb-docs.json at the root, one directory per slug, fixed mtime, uid/gid 0.
  STAGE=$(mktemp -d)
  trap 'rm -rf "$STAGE"; _cleanup' EXIT
  cp -r dist "$STAGE/$SLUG"
  cp "$MANIFEST" "$STAGE/$MANIFEST"
  rm -f "$ASSET_NAME"
  tar --sort=name --mtime='2020-01-01 00:00:00Z' --owner=0 --group=0 --numeric-owner \
      -czf "$ASSET_NAME" -C "$STAGE" "$MANIFEST" "$SLUG"

  echo "✅ $ASSET_NAME ready ($(du -sh "$ASSET_NAME" | cut -f1))"
  echo "   $MANIFEST   → manifest with generated pages"
  echo "   $SLUG/index.html  → entry point"
  exit 0
fi

if [ "$HEADLESS" = true ]; then
  echo "✅ dist/ ready (headless)"
  echo "   dist/index.html      → showcase without nav (headless entry point)"
  echo "   dist/docs/index.html → documentation"
  echo "   Publish: the release workflow hands dist/ + $MANIFEST to actions/publish-docs"
  echo "   Inspect: bash scripts/pack.sh --pack → $ASSET_NAME"
else
  echo "✅ dist/ ready"
  echo "   dist/index.html      → product showcase (entry point)"
  echo "   dist/docs/index.html → documentation"
fi

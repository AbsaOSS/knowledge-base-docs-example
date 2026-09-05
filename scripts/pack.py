#!/usr/bin/env python3
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

"""pack.py — build the docs site for the Knowledge Base.

Usage:
  python scripts/pack.py            # standalone build → dist/
  python scripts/pack.py --headless # headless build → dist/ (what the release publishes)
  python scripts/pack.py --pack     # headless build + local kb-docs.tar.gz for inspection
  python scripts/pack.py --serve    # generate config + live-reload dev server

Every build refreshes `apps[0].pages` in kb-docs.json from the frontmatter of
docs/*.md, so the manifest the publish action reads always matches the built
output.

Packing and publishing is the job of the reusable action
AbsaOSS/knowledge-base/actions/publish-docs (see .github/workflows/pack.yml).
`--pack` mirrors its artifact layout — kb-docs.json + <slug>/ — so a developer
can inspect what the knowledge base will receive without cutting a release.

Prerequisites: pip install -r requirements.txt
               Set SKIP_PIP_INSTALL=1 to bypass (e.g. managed environments where packages are pre-installed)
"""

import atexit
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


# Windows consoles default to a legacy code page that cannot encode the
# progress glyphs printed below; force UTF-8 so a local build does not crash.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


# ── Knowledge base contract (contract/ARTIFACT.md in AbsaOSS/knowledge-base) ──
MANIFEST = "kb-docs.json"
ASSET_NAME = "kb-docs.tar.gz"
KB_VERSION = "1"
HEADLESS_MARKER = 'data-kb-headless="true"'
SIZE_WARN = 20 * 1024 * 1024


# ── Build-time cleanup ────────────────────────────────────────────────────────
def _cleanup():
    for f in ("mkdocs-build.yml", "mkdocs-headless-build.yml"):
        Path(f).unlink(missing_ok=True)

atexit.register(_cleanup)


# ── Helpers ───────────────────────────────────────────────────────────────────
def run(*args, **kwargs):
    """Run a subprocess, raising on non-zero exit."""
    result = subprocess.run(args, **kwargs)
    if result.returncode != 0:
        sys.exit(result.returncode)


def human_size(path: Path) -> str:
    size = path.stat().st_size
    for unit in ("B", "K", "M", "G"):
        if size < 1024:
            return f"{size:.0f}{unit}"
        size /= 1024
    return f"{size:.0f}T"


def parse_frontmatter(md_path: str) -> dict:
    text = Path(md_path).read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            kv = line.split(":", 1)
            if len(kv) == 2:
                k, v = kv[0].strip(), kv[1].strip()
                meta[k] = int(v) if v.isdigit() else v
    return meta


def output_path(md_rel: str) -> str:
    """Map a docs/-relative source path to its built HTML path inside dist/.

    MkDocs (use_directory_urls) renders index.md → index.html and any other
    page → <page>/index.html, preserving subdirectories.
    """
    rel = Path(md_rel).with_suffix("").as_posix()
    if rel == "index":
        return "docs/index.html"
    if rel.endswith("/index"):
        rel = rel[: -len("/index")]
    return f"docs/{rel}/index.html"


# ── Auto-generate nav from frontmatter ───────────────────────────────────────
def auto_generate_nav(docs_dir="docs"):
    """Scan docs/ for .md files, read frontmatter, build nav sorted by order."""
    docs_path = Path(docs_dir)
    pages = []

    for md_file in docs_path.rglob("*.md"):
        rel = md_file.relative_to(docs_path).as_posix()
        fm = parse_frontmatter(str(md_file))
        pages.append({
            "file": rel,
            "title": fm.get("title", md_file.stem.replace("-", " ").title()),
            "order": fm.get("order", 999),
            "section": fm.get("section"),
        })

    pages.sort(key=lambda p: p["order"])

    top_level = []
    sections = {}
    section_min_order = {}

    for page in pages:
        entry = {page["title"]: page["file"]}
        sect = page["section"]
        if sect:
            sections.setdefault(sect, []).append(entry)
            section_min_order[sect] = min(section_min_order.get(sect, 999), page["order"])
        else:
            top_level.append(entry)

    nav = list(top_level)

    for sect_name in sorted(sections, key=lambda s: section_min_order[s]):
        nav.append({sect_name: sections[sect_name]})

    return nav


# ── Generate build configs ────────────────────────────────────────────────────
def generate_build_configs():
    import yaml

    cfg = yaml.safe_load(Path("mkdocs.yml").read_text(encoding="utf-8"))

    nav = auto_generate_nav(cfg.get("docs_dir", "docs"))
    print(f"  Auto-generated nav with {sum(len(v) if isinstance(v, dict) and isinstance(list(v.values())[0], list) else 1 for v in nav)} page(s)")

    cfg["nav"] = nav

    Path("mkdocs-build.yml").write_text(
        yaml.dump(cfg, default_flow_style=False, allow_unicode=True), encoding="utf-8"
    )

    Path("mkdocs-headless-build.yml").write_text(
        "INHERIT: mkdocs-build.yml\n\nextra:\n  headless: true\n", encoding="utf-8"
    )


# ── HTML page wrapper for showcase content ───────────────────────────────────
SHOWCASE_WRAPPER = """\
<!DOCTYPE html>
<html lang="en"{html_attrs}>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Showcase</title>
  <link rel="stylesheet" href="docs/style.css" />
  <link rel="stylesheet" href="showcase.css" />
</head>
<body>
{content}
</body>
</html>"""


# ── Render showcase from data ────────────────────────────────────────────────
def render_showcase(headless=False):
    import yaml

    data_path = Path("data/showcase.yml")
    if not data_path.exists():
        print("  ⚠ data/showcase.yml missing — skipping showcase render")
        return

    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))
    content = data.get("content", "")

    if not content:
        print("  ⚠ data/showcase.yml has no content — skipping showcase render")
        return

    if headless:
        content = re.sub(
            r"<!-- ── Navigation ── -->\s*<nav[^>]*>.*?</nav>\s*<!-- ── /Navigation ── -->",
            "", content, flags=re.DOTALL
        )

    html_attrs = f" {HEADLESS_MARKER}" if headless else ""
    html = SHOWCASE_WRAPPER.format(html_attrs=html_attrs, content=content)
    Path("dist/index.html").write_text(html, encoding="utf-8")

    if Path("showcase.css").exists():
        shutil.copy2("showcase.css", "dist/showcase.css")

    # The CMS is part of the standalone site only. It is not documentation, and
    # its pages would fail the knowledge base's headless verification.
    if not headless and Path("admin").is_dir():
        shutil.copytree("admin", "dist/admin", dirs_exist_ok=True)


# ── Pages manifest → kb-docs.json ─────────────────────────────────────────────
def generate_pages():
    """Derive the `pages` navigation manifest from the auto-generated nav."""
    import yaml

    cfg = yaml.safe_load(Path("mkdocs-build.yml").read_text(encoding="utf-8"))
    nav = cfg.get("nav", [])

    pages = []
    order_counter = [1]

    def add_entries(items, section=None):
        for item in items:
            if isinstance(item, dict):
                for label, value in item.items():
                    if isinstance(value, str):
                        fm = parse_frontmatter(f"docs/{value}")
                        entry = {
                            "title": fm.get("title", label),
                            "path": output_path(value),
                            "order": fm.get("order", order_counter[0]),
                        }
                        if section:
                            entry["section"] = section
                        elif fm.get("section"):
                            entry["section"] = fm["section"]
                        pages.append(entry)
                        order_counter[0] += 1
                    elif isinstance(value, list):
                        add_entries(value, section=label)

    add_entries(nav)
    return pages


def read_manifest() -> dict:
    path = Path(MANIFEST)
    if not path.exists():
        print(f"❌ {MANIFEST} missing — see docs/publishing.md for its shape")
        sys.exit(1)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    apps = manifest.get("apps")
    if manifest.get("kbVersion") != KB_VERSION or not isinstance(apps, list) or not apps:
        print(f'❌ {MANIFEST} must have "kbVersion": "{KB_VERSION}" and a non-empty "apps" list')
        sys.exit(1)
    if len(apps) != 1:
        print(f"❌ {MANIFEST} declares {len(apps)} apps; this template builds exactly one")
        sys.exit(1)
    return manifest


def update_manifest_pages() -> dict:
    """Write the computed `pages` into apps[0] of kb-docs.json, in place.

    kb-docs.json is the file the publish action reads, so the pages list has to
    live there rather than in dist/. Only `apps[0].pages` is touched; every
    other field is the author's.
    """
    manifest = read_manifest()
    pages = generate_pages()
    manifest["apps"][0]["pages"] = pages
    Path(MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {len(pages)} page(s) written to {MANIFEST} (apps[0].pages)")
    return manifest


# ── Local packing (mirrors actions/publish-docs) ─────────────────────────────
def verify_headless(dist: Path, app: dict):
    """Cheap pre-flight of the checks the publish action runs (HEADLESS_RULES.md)."""
    errors = []
    entry = app.get("entryPoint", "index.html")
    if not (dist / entry).exists():
        errors.append(f'entryPoint "{entry}" does not exist in dist/')
    for page in app.get("pages", []):
        if not (dist / page["path"]).exists():
            errors.append(f'pages entry "{page["title"]}" points at "{page["path"]}", which was not built')
    for html_file in sorted(dist.rglob("*.html")):
        html = html_file.read_text(encoding="utf-8", errors="replace")
        where = html_file.relative_to(dist).as_posix()
        if HEADLESS_MARKER not in html:
            errors.append(f"{where}: missing {HEADLESS_MARKER} on <html>")
        if re.search(r"<base\b", html, re.IGNORECASE):
            errors.append(f"{where}: contains a <base> element")
        absolute = [
            u for u in re.findall(r'\b(?:href|src|action|poster)="(/[^/"][^"]*)"', html)
            if not u.startswith("/favicon")
        ]
        if absolute:
            errors.append(f'{where}: {len(absolute)} root-relative URL(s), e.g. "{absolute[0]}"')
    if errors:
        print("❌ dist/ does not satisfy the knowledge base headless rules:")
        for e in errors:
            print(f"   • {e}")
        sys.exit(1)


def pack_artifact(manifest: dict):
    """Pack kb-docs.json + <slug>/ (= dist/) into kb-docs.tar.gz.

    Same layout and the same deterministic metadata (fixed mtime, uid/gid 0,
    members sorted by name) as the publish action, so the local artifact is
    byte-comparable with a released one.
    """
    app = manifest["apps"][0]
    slug = app["slug"]
    dist = Path("dist")
    verify_headless(dist, app)

    epoch = 1577836800  # 2020-01-01T00:00:00Z, matches the action

    def normalise(info: tarfile.TarInfo) -> tarfile.TarInfo:
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        info.mtime = epoch
        return info

    out = Path(ASSET_NAME)
    out.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        shutil.copytree(dist, stage / slug)
        manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

        with tarfile.open(out, "w:gz") as tar:
            info = tarfile.TarInfo(MANIFEST)
            info.size = len(manifest_bytes)
            tar.addfile(normalise(info), io.BytesIO(manifest_bytes))

            root = stage / slug
            members = sorted(root.rglob("*"), key=lambda p: p.relative_to(stage).as_posix())
            tar.add(root, arcname=slug, recursive=False, filter=normalise)
            for member in members:
                tar.add(member, arcname=member.relative_to(stage).as_posix(),
                        recursive=False, filter=normalise)

    size = out.stat().st_size
    print(f"✅ {ASSET_NAME} ready ({human_size(out)})")
    print(f"   {MANIFEST}   → manifest with {len(app.get('pages', []))} page(s)")
    print(f"   {slug}/{app.get('entryPoint', 'index.html')}  → entry point")
    if size > SIZE_WARN:
        print(f"⚠  Artifact exceeds the {SIZE_WARN // (1024 * 1024)} MB target — every knowledge base build downloads it")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    headless = False
    serve = False
    pack = False
    for arg in sys.argv[1:]:
        if arg == "--headless":
            headless = True
        elif arg == "--serve":
            serve = True
        elif arg == "--pack":
            pack = True
            headless = True  # only a headless build is a valid knowledge base artifact
        else:
            print(f"Unknown argument: {arg}")
            sys.exit(1)

    if os.environ.get("SKIP_PIP_INSTALL", "0") != "1":
        print("▶ Installing Python dependencies...")
        run(sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q", "--break-system-packages")

    if serve:
        print("▶ Generating build config for dev server...")
        generate_build_configs()
        print("▶ Starting dev server (mkdocs serve)...")
        run(sys.executable, "-m", "mkdocs", "serve", "-f", "mkdocs-build.yml")
        return

    print("▶ Cleaning dist/...")
    shutil.rmtree("dist", ignore_errors=True)

    print("▶ Generating build configs...")
    generate_build_configs()

    mode = " (headless)" if headless else ""
    print(f"▶ Building docs{mode}...")
    run(sys.executable, "-m", "mkdocs", "build",
        "-f", "mkdocs-headless-build.yml" if headless else "mkdocs-build.yml")

    if not Path("dist/docs/index.html").exists():
        print("❌ dist/docs/index.html missing — build failed")
        sys.exit(1)

    print(f"▶ Rendering showcase{mode}...")
    render_showcase(headless=headless)

    print(f"▶ Updating {MANIFEST} pages manifest...")
    manifest = update_manifest_pages()

    if pack:
        print(f"▶ Packing {ASSET_NAME} (local preview of the publish action)...")
        pack_artifact(manifest)
        return

    print(f"✅ dist/ ready{mode}")
    if headless:
        print("   dist/index.html      → showcase without nav (headless entry point)")
        print("   dist/docs/index.html → documentation")
        print(f"   Publish: the release workflow hands dist/ + {MANIFEST} to actions/publish-docs")
        print(f"   Inspect: python scripts/pack.py --pack → {ASSET_NAME}")
    else:
        print("   dist/index.html      → product showcase (entry point)")
        print("   dist/docs/index.html → documentation")


if __name__ == "__main__":
    main()

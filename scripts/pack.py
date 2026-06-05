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

"""pack.py — build the docs site and package the release artifact.

Usage:
  python scripts/pack.py            # standalone
  python scripts/pack.py --headless # headless (no top nav)

Output: dist.tar.gz  (contains dist/ + marketplace.json)

Prerequisites: pip install -r requirements.txt
               Set SKIP_PIP_INSTALL=1 to bypass (e.g. managed environments where packages are pre-installed)
"""

import atexit
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path


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


# ── Generate build configs ────────────────────────────────────────────────────
def generate_build_configs():
    import yaml  # available after pip install

    cfg = yaml.safe_load(Path("mkdocs.yml").read_text(encoding="utf-8"))

    wiki_pages = sorted(Path("docs/wiki").glob("*.md")) if Path("docs/wiki").exists() else []
    if wiki_pages:
        wiki_nav = [
            {p.stem.replace("-", " ").replace("_", " "): f"wiki/{p.name}"}
            for p in wiki_pages
        ]
        cfg.setdefault("nav", []).append({"Wiki": wiki_nav})
        print(f"  Added {len(wiki_pages)} wiki page(s) to nav")

    Path("mkdocs-build.yml").write_text(
        yaml.dump(cfg, default_flow_style=False, allow_unicode=True), encoding="utf-8"
    )

    Path("mkdocs-headless-build.yml").write_text(
        "INHERIT: mkdocs-build.yml\n\nextra:\n  headless: true\n", encoding="utf-8"
    )


# ── Generate marketplace.json ─────────────────────────────────────────────────
def generate_marketplace_json():
    import yaml

    cfg = yaml.safe_load(Path("mkdocs-build.yml").read_text(encoding="utf-8"))
    nav = cfg.get("nav", [])

    pages = []
    order_counter = [1]  # list so nested fn can mutate it

    def add_entries(items, section=None):
        for item in items:
            if isinstance(item, dict):
                for label, value in item.items():
                    if isinstance(value, str):
                        fm = parse_frontmatter(f"docs/{value}")
                        stem = Path(value).stem
                        out = "docs/index.html" if stem == "index" else f"docs/{stem}/index.html"
                        entry = {
                            "title": fm.get("title", label),
                            "path": out,
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

    manifest = json.loads(Path("marketplace.json").read_text(encoding="utf-8"))
    manifest["pages"] = pages
    Path("dist/marketplace.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"  {len(pages)} page(s) written to dist/marketplace.json")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    headless = False
    for arg in sys.argv[1:]:
        if arg == "--headless":
            headless = True
        else:
            print(f"Unknown argument: {arg}")
            sys.exit(1)

    if os.environ.get("SKIP_PIP_INSTALL", "0") != "1":
        print("▶ Installing Python dependencies...")
        run(sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q", "--break-system-packages")

    print("▶ Cleaning dist/...")
    shutil.rmtree("dist", ignore_errors=True)

    print("▶ Generating build configs...")
    generate_build_configs()

    if headless:
        print("▶ Building docs (headless)...")
        run(sys.executable, "-m", "mkdocs", "build", "-f", "mkdocs-headless-build.yml")

        if not Path("dist/docs/index.html").exists():
            print("❌ dist/docs/index.html missing — build failed")
            sys.exit(1)

        print("▶ Copying showcase (without nav) as entry point...")
        html = Path("showcase.html").read_text(encoding="utf-8")
        html = re.sub(
            r"<!-- ── Navigation ── -->\s*<nav[^>]*>.*?</nav>", "", html, flags=re.DOTALL
        )
        Path("dist/index.html").write_text(html, encoding="utf-8")

        print("▶ Generating dist/marketplace.json with pages manifest...")
        generate_marketplace_json()

        print("▶ Packaging (headless)...")
        with tarfile.open("dist.tar.gz", "w:gz") as tar:
            tar.add("dist")
            tar.add("marketplace.json")

        size = human_size(Path("dist.tar.gz"))
        print(f"✅ dist.tar.gz ready ({size}) [headless]")
        print("   dist/index.html      → showcase without nav (headless entry point)")
        print("   dist/docs/index.html → documentation")

    else:
        print("▶ Building docs...")
        run(sys.executable, "-m", "mkdocs", "build", "-f", "mkdocs-build.yml")

        if not Path("dist/docs/index.html").exists():
            print("❌ dist/docs/index.html missing — build failed")
            sys.exit(1)

        print("▶ Copying showcase as entry point...")
        shutil.copy2("showcase.html", "dist/index.html")

        print("▶ Generating dist/marketplace.json with pages manifest...")
        generate_marketplace_json()

        print("▶ Packaging...")
        with tarfile.open("dist.tar.gz", "w:gz") as tar:
            tar.add("dist")
            tar.add("marketplace.json")

        size = human_size(Path("dist.tar.gz"))
        print(f"✅ dist.tar.gz ready ({size})")
        print("   dist/index.html      → product showcase (entry point)")
        print("   dist/docs/index.html → documentation")


if __name__ == "__main__":
    main()

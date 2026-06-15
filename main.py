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

"""mkdocs-macros module — reusable components for documentation pages.

Macros are usable directly inside any docs/*.md file, e.g.:

    {{ sharepoint_video('https://absa.sharepoint.com/.../video.mp4', title='Demo') }}

Docs: https://mkdocs-macros-plugin.readthedocs.io/
"""

import html


def define_env(env):
    """Register macros with the mkdocs-macros plugin."""

    @env.macro
    def sharepoint_video(url, title="SharePoint video", ratio="56.25%"):
        """Embed a SharePoint / Microsoft Stream video as a responsive iframe.

        Args:
            url:   The SharePoint share/embed URL of the video.
            title: Accessible iframe title (shown to screen readers).
            ratio: Aspect-ratio padding. "56.25%" = 16:9, "75%" = 4:3.

        Usage in a .md page:
            {{ sharepoint_video('https://absa.sharepoint.com/.../video.mp4') }}

        Tip: in SharePoint use "Share" → "Embed" and paste the src URL. A plain
        share link usually works too; append "&embed=true" if the player does
        not load.
        """
        safe_url = html.escape(str(url), quote=True)
        safe_title = html.escape(str(title), quote=True)
        return (
            f'<div class="sp-embed" style="position:relative;width:100%;'
            f'padding-bottom:{ratio};height:0;overflow:hidden;margin:1.5rem 0;'
            f'border-radius:8px;background:#000;">'
            f'<iframe src="{safe_url}" title="{safe_title}" '
            f'style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" '
            f'allowfullscreen '
            f'allow="autoplay; fullscreen; encrypted-media; picture-in-picture" '
            f'loading="lazy"></iframe></div>'
        )

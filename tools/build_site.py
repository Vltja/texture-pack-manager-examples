#!/usr/bin/env python3
"""Render docs/API.md as a static GitHub Pages site; no game dependencies needed."""
from html import escape
from pathlib import Path
import re

try:
    from markdown_it import MarkdownIt
except ImportError:
    raise SystemExit("Install documentation dependencies: python3 -m pip install -r requirements-docs.txt")

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/Vltja/texture-pack-manager-examples"


def main():
    headings = []
    used = {}
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    original = md.renderer.rules.get("heading_open")

    def heading(tokens, index, options, env):
        title = tokens[index + 1].content
        base = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = used.get(base, 0)
        used[base] = count + 1
        anchor = base if not count else f"{base}-{count}"
        tokens[index].attrSet("id", anchor)
        if tokens[index].tag == "h2" and title != "Contents":
            headings.append((anchor, title))
        return original(tokens, index, options, env) if original else md.renderer.renderToken(tokens, index, options, env)

    md.renderer.rules["heading_open"] = heading
    rendered = md.render((ROOT / "docs/API.md").read_text(encoding="utf-8"))
    navigation = "".join(f'<a href="#{escape(a)}">{escape(t)}</a>' for a, t in headings)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Texture Pack Manager API v1: build a lightweight Hytale texture-pack mod, use native paths and manage server-wide priority.">
<title>Texture Pack Manager — Developer Guide</title><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#guide">Skip to API guide</a>
<aside><a class="brand" href="#">Texture Pack<br><strong>Manager</strong></a><p class="version">DEVELOPER GUIDE · API v1</p>
<nav aria-label="API sections">{navigation}</nav>
<div class="side-links"><a href="{REPO}">Example repository ↗</a><a href="https://www.curseforge.com/hytale/mods/texture-pack-manager">Manager on CurseForge ↗</a></div></aside>
<main><header class="intro"><p class="eyebrow">BUILD YOUR OWN TEXTURE PACK</p><h1>One registration.<br>Native texture paths.</h1>
<p>Start with a small, downloadable example. The Manager handles activation, order and server-wide texture selection.</p>
<div class="actions"><a class="primary" href="{REPO}/archive/refs/tags/v1.0.0.zip">Download example source</a><a href="{REPO}/releases/tag/v1.0.0">Demo JAR &amp; build instructions</a></div>
<p class="notice">Requires JDK 25+, Python 3.9+, HytaleServer.jar and the separate Manager 0.3.1 JAR. No Manager or SDK classes are bundled.</p></header>
<article id="guide">{rendered}</article>
<footer>© 2026 Vitja · <a href="{REPO}/blob/main/LICENSE.md">Example reuse permission</a> · <a href="{REPO}/issues">Report a documentation issue</a></footer>
</main></body></html>'''
    (ROOT / "docs/index.html").write_text(page, encoding="utf-8")
    (ROOT / "docs/.nojekyll").touch()
    print(f"Rendered API guide with {len(headings)} section links")


if __name__ == "__main__":
    main()

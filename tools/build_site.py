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


def render_guide(source):
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
    rendered = md.render((ROOT / source).read_text(encoding="utf-8"))
    return rendered, headings


def render_beginner_page(source, destination, language, title, description, back_label):
    rendered, headings = render_guide(source)
    # Markdown sources retain working GitHub links; HTML points at the generated site.
    rendered = rendered.replace('href="API.md"', 'href="index.html"')
    navigation = "".join(f'<a href="#{escape(a)}">{escape(t)}</a>' for a, t in headings)
    other = "beginner-en.html" if language == "de" else "beginner-de.html"
    other_label = "English guide" if language == "de" else "Deutsche Anleitung"
    page = f'''<!doctype html>
<html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(description)}">
<title>{escape(title)}</title><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#guide">{escape(title)}</a>
<aside><a class="brand" href="index.html">Texture Pack<br><strong>Manager</strong></a><p class="version">BEGINNER GUIDE · API v1</p>
<nav aria-label="Guide sections">{navigation}</nav>
<div class="side-links"><a href="index.html">{escape(back_label)}</a><a href="{other}">{other_label}</a><a href="{REPO}">GitHub source ↗</a></div></aside>
<main><header class="intro"><p class="eyebrow">TEXTURE PACK MANAGER · STARTER</p><h1>{escape(title)}</h1>
<p>{escape(description)}</p>
<div class="actions"><a class="primary" href="{REPO}/archive/refs/heads/main.zip">Source ZIP herunterladen / Download source</a>
<a href="index.html">{escape(back_label)}</a><a href="{other}">{other_label}</a></div></header>
<article id="guide">{rendered}</article>
<footer>© 2026 Vitja · <a href="{REPO}/blob/main/{source}">Markdown source</a> · <a href="{REPO}/issues">Documentation feedback</a></footer>
</main></body></html>'''
    (ROOT / destination).write_text(page, encoding="utf-8")
    return len(headings)


def main():
    rendered, headings = render_guide("docs/API.md")
    rendered = rendered.replace(f'{REPO}/blob/main/docs/BEGINNER_DE.md', "beginner-de.html")
    rendered = rendered.replace(f'{REPO}/blob/main/docs/BEGINNER_EN.md', "beginner-en.html")
    navigation = "".join(f'<a href="#{escape(a)}">{escape(t)}</a>' for a, t in headings)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Texture Pack Manager API v1: build a lightweight Hytale texture-pack mod, use native paths and manage server-wide priority.">
<title>Texture Pack Manager — Developer Guide</title><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#guide">Skip to API guide</a>
<aside><a class="brand" href="#">Texture Pack<br><strong>Manager</strong></a><p class="version">DEVELOPER GUIDE · API v1</p>
<nav aria-label="API sections">{navigation}</nav>
<div class="side-links"><a href="beginner-de.html">Anfänger-Anleitung (DE)</a><a href="beginner-en.html">Beginner guide (EN)</a><a href="{REPO}">Example repository ↗</a><a href="https://www.curseforge.com/hytale/mods/texture-pack-manager">Manager on CurseForge ↗</a></div></aside>
<main><header class="intro"><p class="eyebrow">BUILD YOUR OWN TEXTURE PACK</p><h1>One registration.<br>Native texture paths.</h1>
<p>Start with a small, downloadable example. The Manager handles activation, order and server-wide texture selection.</p>
<div class="actions"><a class="primary" href="beginner-en.html">Beginner guide (EN)</a><a href="beginner-de.html">Anfänger-Anleitung (DE)</a><a href="{REPO}/archive/refs/heads/main.zip">Download example source</a><a href="{REPO}/releases/tag/v1.0.0">Demo JAR &amp; build instructions</a></div>
<p class="notice">Requires JDK 25+, Python 3.9+, HytaleServer.jar and the separate Manager 0.3.1 JAR. No Manager or SDK classes are bundled.</p></header>
<article id="guide">{rendered}</article>
<footer>© 2026 Vitja · <a href="{REPO}/blob/main/LICENSE.md">Example reuse permission</a> · <a href="{REPO}/issues">Report a documentation issue</a></footer>
</main></body></html>'''
    (ROOT / "docs/index.html").write_text(page, encoding="utf-8")
    (ROOT / "docs/.nojekyll").touch()
    de = render_beginner_page("docs/BEGINNER_DE.md", "docs/beginner-de.html", "de",
                             "Dein erstes Hytale-Texture-Pack",
                             "Schritt für Schritt: Bilder ersetzen, eindeutige Mod-ID vergeben, JAR bauen und auf dem Server testen.",
                             "Zum technischen API-Leitfaden")
    en = render_beginner_page("docs/BEGINNER_EN.md", "docs/beginner-en.html", "en",
                             "Your first Hytale texture pack",
                             "Step by step: replace images, give your pack a unique identity, build the JAR and test it on a server.",
                             "Back to the API guide")
    print(f"Rendered API guide ({len(headings)} sections) and beginner guides (DE {de}, EN {en} sections)")


if __name__ == "__main__":
    main()

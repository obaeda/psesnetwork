#!/usr/bin/env python3
"""Small dependency-free quality gate for the static PSES website."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
INDEXABLE_REDIRECTS = {
    "ai.html",
    "docs.html",
    "market.html",
    "network.html",
    "wallet.html",
    "status/index.html",
    "guides/index.html",
    "en/guides/index.html",
    "404.html",
}
IGNORED_SCHEMES = {"mailto", "tel", "intent"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.images: list[str] = []
        self.scripts: list[dict[str, str | None]] = []
        self.meta: list[dict[str, str | None]] = []
        self.link_tags: list[dict[str, str | None]] = []
        self.title_depth = 0
        self.title = ""
        self.current_json_ld: list[str] | None = None
        self.json_ld: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "a" and data.get("href"):
            self.links.append(str(data["href"]))
        if tag == "img" and data.get("src"):
            self.images.append(str(data["src"]))
        if tag == "meta":
            self.meta.append(data)
        if tag == "link":
            self.link_tags.append(data)
        if tag == "title":
            self.title_depth += 1
        if tag == "script" and data.get("type") == "application/ld+json":
            self.current_json_ld = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.title_depth:
            self.title_depth -= 1
        if tag == "script" and self.current_json_ld is not None:
            self.json_ld.append("".join(self.current_json_ld))
            self.current_json_ld = None

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title += data
        if self.current_json_ld is not None:
            self.current_json_ld.append(data)


def target_for(url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme in IGNORED_SCHEMES or parsed.scheme in {"http", "https"}:
        return None
    path = unquote(parsed.path)
    if not path.startswith("/"):
        return None
    target = ROOT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    return target


def main() -> int:
    errors: list[str] = []
    html_files = sorted(ROOT.rglob("*.html"))
    if not html_files:
        errors.append("No HTML files found")

    for page in html_files:
        relative = page.relative_to(ROOT).as_posix()
        parser = PageParser()
        try:
            parser.feed(page.read_text(encoding="utf-8"))
        except Exception as error:  # pragma: no cover - reports damaged input
            errors.append(f"{relative}: HTML parser failed: {error}")
            continue

        if not parser.title.strip():
            errors.append(f"{relative}: missing title")

        redirect_or_404 = relative in INDEXABLE_REDIRECTS
        meta_by_name = {str(item.get("name", "")).lower(): item for item in parser.meta}
        if not redirect_or_404 and not meta_by_name.get("description", {}).get("content"):
            errors.append(f"{relative}: missing meta description")

        canonical = [item for item in parser.link_tags if item.get("rel") == "canonical"]
        if not redirect_or_404 and len(canonical) != 1:
            errors.append(f"{relative}: expected one canonical, got {len(canonical)}")

        for raw_json in parser.json_ld:
            try:
                json.loads(raw_json)
            except json.JSONDecodeError as error:
                errors.append(f"{relative}: invalid JSON-LD: {error}")

        for url in parser.links + parser.images:
            target = target_for(url)
            if target is not None and not target.exists():
                errors.append(f"{relative}: broken local target {url}")

    for json_name in ("knowledge.json", "site.webmanifest"):
        try:
            json.loads((ROOT / json_name).read_text(encoding="utf-8"))
        except Exception as error:
            errors.append(f"{json_name}: invalid JSON: {error}")

    for xml_name in ("sitemap.xml", "feed.xml"):
        try:
            ET.parse(ROOT / xml_name)
        except Exception as error:
            errors.append(f"{xml_name}: invalid XML: {error}")

    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for loc in sitemap.findall("s:url/s:loc", namespace):
        url = (loc.text or "").strip()
        parsed = urlparse(url)
        if parsed.netloc != "psesnetwork.com":
            errors.append(f"sitemap.xml: unexpected host in {url}")
            continue
        target = ROOT / parsed.path.lstrip("/")
        if parsed.path.endswith("/"):
            target /= "index.html"
        if not target.exists():
            errors.append(f"sitemap.xml: target does not exist for {url}")

    forbidden_live_phrases = (
        "Useful Proof of Work",
        "Distributed Compute & AI",
        "شبكة بلوك تشين حقيقية",
        "Open Testnet",
    )
    for page in html_files:
        content = page.read_text(encoding="utf-8")
        for phrase in forbidden_live_phrases:
            if phrase in content:
                errors.append(f"{page.relative_to(ROOT)}: cancelled-project text remains: {phrase}")

    if errors:
        print(f"Site validation failed with {len(errors)} issue(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Site validation passed: {len(html_files)} HTML pages, JSON, XML, links and legacy-content gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

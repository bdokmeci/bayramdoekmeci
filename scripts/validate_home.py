"""Check homepage navigation against the actual pages, assets and sitemap."""

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://bayramdoekmeci.de"


class HomeParser(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links = []
        self.assets = []
        self.ids = []
        self.headings = []
        self.schema = ""
        self.in_schema = False
        self.feed(source)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "img" or (tag == "script" and "src" in attrs):
            self.assets.append(attrs.get("src", ""))
        if tag == "link" and attrs.get("rel") in ("stylesheet", "icon", "preload", "alternate"):
            self.assets.append(attrs.get("href", ""))
        if tag == "h1":
            self.headings.append(tag)
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_schema = True

    def handle_data(self, data):
        if self.in_schema:
            self.schema += data

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_schema = False


def main():
    page = HomeParser((ROOT / "index.html").read_text(encoding="utf-8"))
    pages = {"/" + path.parent.name + "/" for path in ROOT.glob("*/index.html") if path.parent.name != "en"}
    errors = []
    for missing in sorted(pages - set(page.links)):
        errors.append(f"Subpage missing from homepage: {missing}")
    for href in page.links + page.assets:
        url = urlsplit(href)
        if url.scheme or url.netloc:
            continue
        if url.path:
            target = ROOT / url.path.lstrip("/")
            if url.path.endswith("/"):
                target /= "index.html"
            if not target.is_file():
                errors.append(f"Broken local link or asset: {href}")
        elif url.fragment and url.fragment not in page.ids:
            errors.append(f"Missing anchor: {href}")
    if len(page.headings) != 1:
        errors.append("Homepage must have one h1")
    if len(set(page.ids)) != len(page.ids):
        errors.append("Duplicate HTML IDs")
    graph = json.loads(page.schema)["@graph"]
    listing = next(node for node in graph if node["@type"] == "ItemList")
    listed = {urlsplit(item["url"]).path for item in listing["itemListElement"]}
    if listed != pages - {"/impressum/", "/datenschutz/"}:
        errors.append("Structured service list does not match the actual service pages")
    if listing["numberOfItems"] != len(listed):
        errors.append("Structured service count is incorrect")
    sitemap = ElementTree.parse(ROOT / "sitemap.xml")
    urls = {node.text for node in sitemap.findall(".//{*}loc")}
    for path in pages | {"/"}:
        if ORIGIN + path not in urls:
            errors.append(f"Page missing from sitemap: {path}")
    for path in pages:
        icon = ROOT / "assets" / "icons" / (path.strip("/") + ".svg")
        if not icon.is_file():
            errors.append(f"Missing original icon: {path}")
        else:
            ElementTree.parse(icon)
    for error in errors:
        print("FAIL", error)
    print(f"{len(pages)} subpages, {len(listed)} services, links, anchors, assets, icons and sitemap: {len(errors)} issues.")
    from validate_locales import main as validate_locales
    return bool(errors) | validate_locales()


if __name__ == "__main__":
    raise SystemExit(main())

"""Check the site's JSON-LD and the Google requirements used by these pages.

Run with: python scripts/validate_structured_data.py
This is a local regression check, not a replacement for Google's Rich Results Test.
"""

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://bayramdoekmeci.de/"


class PageParser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.visible = []
        self.canonicals = []
        self.in_schema = False
        self.hidden_depth = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style"):
            self.hidden_depth += 1
        if tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self.in_schema = True
            self.blocks.append("")
        if tag == "link" and "canonical" in attrs.get("rel", "").split():
            self.canonicals.append(attrs.get("href"))

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_schema = False
        if tag in ("script", "style"):
            self.hidden_depth = max(0, self.hidden_depth - 1)

    def handle_data(self, data):
        if self.in_schema:
            self.blocks[-1] += data
        elif not self.hidden_depth:
            self.visible.append(data)


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def normalize(value):
    return " ".join(value.split())


def validate_page(path, source):
    page = PageParser(source)
    errors = []
    relative = path.relative_to(ROOT).as_posix()
    canonical = ORIGIN + relative.removesuffix("index.html")
    if page.canonicals != [canonical]:
        errors.append(f"Expected one canonical URL: {canonical}")
    if not page.blocks:
        errors.append("No JSON-LD found")
    visible = normalize(" ".join(page.visible))
    for number, block in enumerate(page.blocks, 1):
        try:
            data = json.loads(block, object_pairs_hook=unique_keys)
        except ValueError as error:
            errors.append(f"JSON-LD block {number}: {error}")
            continue
        if not isinstance(data, dict) or data.get("@context") != "https://schema.org":
            errors.append("Expected a Schema.org JSON-LD object")
            continue
        nodes = data.get("@graph", [data])
        ids = {node["@id"] for node in nodes if "@id" in node}
        for node in nodes:
            kind = node.get("@type")
            if kind == "ProfessionalService":
                errors.append("ProfessionalService is deprecated; use the appropriate current business type")
            if kind in ("LocalBusiness", "ProfessionalService"):
                if not node.get("name") or not node.get("address"):
                    errors.append("LocalBusiness requires name and address")
                if "availableLanguage" in node:
                    errors.append("Put availableLanguage on a ContactPoint, not LocalBusiness")
            if kind == "BreadcrumbList":
                items = node.get("itemListElement", [])
                if len(items) < 2:
                    errors.append("Google breadcrumbs require at least two ListItems")
                if [item.get("position") for item in items] != list(range(1, len(items) + 1)):
                    errors.append("Breadcrumb positions must be consecutive, starting at 1")
                for index, item in enumerate(items):
                    if item.get("@type") != "ListItem" or not item.get("name"):
                        errors.append("Each breadcrumb needs ListItem type and name")
                    url = item.get("item")
                    if not url and index != len(items) - 1:
                        errors.append("Non-final breadcrumb items require a URL")
                    if url:
                        parsed = urlparse(url)
                        if parsed.scheme != "https" or parsed.netloc != "bayramdoekmeci.de":
                            errors.append(f"Unexpected breadcrumb URL: {url}")
                        elif not (ROOT / parsed.path.lstrip("/") / "index.html").is_file():
                            errors.append(f"Breadcrumb URL has no local page: {url}")
            breadcrumb = node.get("breadcrumb", {})
            if "@id" in breadcrumb and breadcrumb["@id"] not in ids:
                errors.append("WebPage references a missing breadcrumb")
            if kind == "FAQPage":
                for question in node.get("mainEntity", []):
                    answer = question.get("acceptedAnswer", {}).get("text", "")
                    if not question.get("name") or not answer:
                        errors.append("FAQ question requires a name and answer")
                    elif normalize(question["name"]) not in visible or normalize(answer) not in visible:
                        errors.append(f"FAQ markup does not match page text: {question['name']}")
    return errors


def main():
    pages = sorted(ROOT.glob("**/index.html"))
    failures = 0
    for path in pages:
        errors = validate_page(path, path.read_text(encoding="utf-8-sig"))
        failures += len(errors)
        print(f"{'FAIL' if errors else 'PASS'} {path.relative_to(ROOT).as_posix()}")
        for error in errors:
            print(f"  {error}")
    print(f"{len(pages)} pages checked; {failures} issues.")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())

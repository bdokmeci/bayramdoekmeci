"""Validate both locales, links, translated surfaces and reproducible text outputs."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree

from localise import ROOT, ORIGIN, pages, route, metadata, EnglishHTML, load_catalogue, ATTR_FIELDS, META_FIELDS, TEXT_FIELDS


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.assets, self.alternates = [], [], [], {}
        self.canonical, self.language, self.locale = [], '', ''
        self.schema, self.blocks, self.mode, self.headings = '', [], '', 0
        self.switches, self.text, self.attributes = [], [], []
        self.stack = []
        self.feed(source)

    def handle_starttag(self, tag, pairs):
        a = dict(pairs)
        if a.get('id'): self.ids.append(a['id'])
        if tag == 'html': self.language = a.get('lang')
        if tag == 'h1': self.headings += 1
        if tag == 'a': self.links.append((a.get('href', ''), a.get('hreflang')))
        if tag in ('img', 'script') and a.get('src'): self.assets.append(a['src'])
        if tag == 'link':
            if a.get('rel') == 'canonical': self.canonical.append(a['href'])
            if a.get('hreflang'): self.alternates[a['hreflang']] = a['href']
            elif a.get('rel') in ('stylesheet', 'icon', 'preload', 'alternate', 'help'): self.assets.append(a['href'])
        if tag == 'meta' and a.get('property') == 'og:locale': self.locale = a.get('content')
        if tag in ('script', 'style'):
            self.mode = 'json' if a.get('type') == 'application/ld+json' else tag
        for key, value in pairs:
            if value and (key in ATTR_FIELDS or key == 'data-search' or (tag == 'meta' and key == 'content' and a.get('name', a.get('property')) in META_FIELDS)):
                self.text.append(value)
            if value and key.startswith(('x-', ':', '@')): self.attributes.append(value)

    def handle_endtag(self, tag):
        if tag == 'script' and self.mode == 'json':
            self.blocks.append(json.loads(self.schema))
            self.schema = ''
        if tag in ('script', 'style'): self.mode = ''

    def handle_data(self, data):
        if self.mode == 'json': self.schema += data
        elif not self.mode and data.strip(): self.text.append(data.strip())


def main():
    errors = []
    german = pages()
    all_paths = german + [ROOT / 'en' / p.relative_to(ROOT) for p in german]
    if len(german) != 28: errors.append(f'Expected 28 German pages, got {len(german)}')
    if len(list(ROOT.glob('**/index.html'))) != 56: errors.append('Expected exactly 56 HTML pages')
    if len(list(ROOT.glob('**/index.md'))) != 56: errors.append('Expected exactly 56 Markdown counterparts')
    parsed = {}
    for path in all_paths:
        if not path.exists():
            errors.append(f'Missing {path.relative_to(ROOT)}')
            continue
        parsed[path] = Page(path.read_text(encoding='utf-8'))
    sitemap = ElementTree.parse(ROOT / 'sitemap.xml')
    sitemap_urls = [x.text for x in sitemap.findall('.//{*}loc')]
    expected_urls = {ORIGIN + '/' + p.relative_to(ROOT).as_posix().removesuffix('index.html') for p in all_paths}
    if set(sitemap_urls) != expected_urls or len(sitemap_urls) != 56: errors.append('Sitemap must contain all 56 unique canonical URLs')
    if set((ROOT / 'links.txt').read_text().splitlines()) != expected_urls: errors.append('links.txt does not match all canonical URLs')
    mapping = json.loads((ROOT / 'scripts/translations/routes.json').read_text())
    if mapping != [{'de': route(p), 'en': '/en' + route(p)} for p in german]: errors.append('Route mapping differs from source pages')
    for folder in (ROOT / 'assets/icons', ROOT / 'en/assets/icons'):
        if len(list(folder.glob('*.svg'))) != 28: errors.append(f'Expected 28 icons in {folder.relative_to(ROOT)}')
        for icon in folder.glob('*.svg'):
            try: ElementTree.parse(icon)
            except ElementTree.ParseError: errors.append(f'Invalid SVG: {icon.relative_to(ROOT)}')
    for path, page in parsed.items():
        rel = path.relative_to(ROOT).as_posix()
        english = rel.startswith('en/')
        lang = 'en' if english else 'de'
        url = ORIGIN + '/' + rel.removesuffix('index.html')
        de_route = '/' + rel.removeprefix('en/').removesuffix('index.html')
        expected = {'de': ORIGIN + de_route, 'en': ORIGIN + '/en' + de_route}
        def fail(message): errors.append(rel + ': ' + message)
        if page.language != lang: fail('Wrong HTML language')
        if page.canonical != [url]: fail('Canonical must be unique and self-referencing')
        if page.alternates != expected: fail('Missing or incorrect reciprocal hreflang links')
        if page.locale != ('en_GB' if english else 'de_DE'): fail('Wrong Open Graph locale')
        if page.headings != 1: fail('Expected one H1')
        if len(page.ids) != len(set(page.ids)): fail('Duplicate IDs')
        switches = {language: urljoin(url, href) for href, language in page.links if language}
        if switches != expected: fail('Missing equivalent-page language switcher')
        for href, hreflang in page.links + [(a, None) for a in page.assets]:
            if not href or href.startswith(('data:', 'mailto:', 'tel:')): continue
            dest = urlsplit(urljoin(url, href))
            if dest.netloc != 'bayramdoekmeci.de': continue
            target = ROOT / unquote(dest.path).lstrip('/')
            if dest.path.endswith('/'): target /= 'index.html'
            if not target.is_file():
                fail('Broken local link/asset: ' + href)
            elif dest.fragment and target.suffix == '.html' and target in parsed and unquote(dest.fragment) not in parsed[target].ids:
                fail('Broken anchor: ' + href)
            if english and target.suffix in ('.html', '.md') and not dest.path.startswith('/en/') and hreflang != 'de':
                fail('English navigation returns to German: ' + href)
        md = path.with_suffix('.md')
        if not md.exists(): fail('Missing Markdown counterpart')
        else:
            markdown = md.read_text(encoding='utf-8')
            if f'url: "{url}"' not in markdown: fail('Markdown URL differs from canonical')
            if english:
                title, description = metadata(path.read_text(encoding='utf-8'))
                if 'title: ' + json.dumps(title, ensure_ascii=False) not in markdown: fail('Markdown title differs from HTML')
                if 'description: ' + json.dumps(description, ensure_ascii=False) not in markdown: fail('Markdown description differs from HTML')
            for href in re.findall(r'\]\(<?([^\s)>]+)>?\)', markdown):
                dest = urlsplit(urljoin(url, href))
                if dest.netloc != 'bayramdoekmeci.de': continue
                target = ROOT / unquote(dest.path).lstrip('/')
                if dest.path.endswith('/'): target /= 'index.html'
                if not target.is_file(): fail('Broken Markdown link: ' + href)
                elif dest.fragment and target in parsed and unquote(dest.fragment) not in parsed[target].ids: fail('Broken Markdown anchor: ' + href)
                if english and target.suffix in ('.html', '.md') and not dest.path.startswith('/en/'): fail('English Markdown returns to German: ' + href)
        for graph in page.blocks:
            for node in graph.get('@graph', [graph]):
                if node.get('@type') in ('WebPage', 'CollectionPage') and str(node.get('inLanguage', '')).split('-')[0] != lang:
                    fail('Wrong page-level JSON-LD language')
        if de_route == '/':
            items = [n for b in page.blocks for n in b.get('@graph', []) if n.get('@type') == 'ItemList']
            services = {expected['en' if english else 'de'] + p.parent.name + '/' for p in german[1:] if p.parent.name not in ('impressum', 'datenschutz')}
            if len(items) != 1 or items[0].get('numberOfItems') != 25 or {i['url'] for i in items[0]['itemListElement']} != services:
                fail('Homepage must list exactly the 25 locale service URLs')
        if english:
            # Exact source-string checks catch untranslated text without flagging names/slugs.
            catalogue = load_catalogue(path.parent.name if path.parent != ROOT / 'en' else 'home')
            for text in page.text:
                source = text.strip()
                if source in catalogue and catalogue[source] != source:
                    fail('Untranslated text: ' + source[:100])
            def display_values(node, field=''):
                if isinstance(node, dict):
                    for key, value in node.items(): yield from display_values(value, key)
                elif isinstance(node, list):
                    for value in node: yield from display_values(value, field)
                elif isinstance(node, str) and field in TEXT_FIELDS:
                    yield node
            for text in (value for graph in page.blocks for value in display_values(graph)):
                if text.strip() in catalogue and catalogue[text.strip()] != text.strip():
                    fail('Untranslated structured data: ' + text[:100])
    for error in errors: print('FAIL', error)
    print(f'Locale checks: {len(parsed)} pages, Markdown, routes, links, assets, language metadata and sitemap; {len(errors)} issues.')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())

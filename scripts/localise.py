"""Deterministic English rendering from German HTML and reviewed text catalogues.

Only the Python standard library is required. Run through build_home.py.
"""
import json
import re
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://bayramdoekmeci.de'
CATALOGUES = ROOT / 'scripts' / 'translations'
TEXT_FIELDS = {'name', 'description', 'jobTitle', 'serviceType', 'audienceType',
               'text', 'contactType', 'headline', 'alternativeHeadline', 'keywords',
               'slogan', 'areaServed', 'knowsAbout'}
ATTR_FIELDS = {'alt', 'title', 'aria-label', 'placeholder', 'aria-description'}
META_FIELDS = {'description', 'og:title', 'og:description', 'twitter:title', 'twitter:description'}
SHARED_IDS = {ORIGIN + '/#' + x for x in ('person', 'business', 'website')}


def pages():
    return [ROOT / 'index.html'] + sorted(p for p in ROOT.glob('*/index.html') if p.parent.name != 'en')


def route(path):
    rel = path.relative_to(ROOT).as_posix().removesuffix('index.html')
    return '/' + rel


def load_catalogue(slug):
    common = json.loads((CATALOGUES / 'common.json').read_text(encoding='utf-8'))
    specific = CATALOGUES / (slug + '.json')
    if not specific.exists():
        raise ValueError(f'Missing English catalogue: {specific.name}')
    common.update(json.loads(specific.read_text(encoding='utf-8')))
    return common


def translate(value, catalogue, composite=False):
    stripped = value.strip()
    translated = catalogue.get(stripped)
    if translated is None:
        normal = ' '.join(stripped.split())
        translated = catalogue.get(normal)
    if translated is None and composite:
        translated = stripped
        for source in sorted(catalogue, key=len, reverse=True):
            if source:
                translated = translated.replace(source, catalogue[source])
    if translated is None:
        return value
    start = len(value) - len(value.lstrip())
    end = len(value.rstrip())
    return value[:start] + translated + value[end:]


def english_url(value, source_route):
    if not value or value.startswith('#'):
        return value
    parsed = urlsplit(urljoin(ORIGIN + source_route, value))
    if parsed.netloc != 'bayramdoekmeci.de' or parsed.scheme not in ('http', 'https'):
        return value
    target = parsed.path
    if target.startswith('/en/'):
        return value
    if target.startswith('/assets/icons/'):
        target = '/en' + target
    elif target.startswith('/assets/'):
        pass
    elif target == '/llms.txt' or target.endswith('/index.md') or target in {route(p) for p in pages()} or target.endswith('/index.html'):
        target = '/en' + target
    result = urlunsplit(('', '', target, parsed.query, parsed.fragment))
    return ORIGIN + result if value.startswith(ORIGIN) else result


def translate_schema(node, catalogue, source_route, field=''):
    if isinstance(node, list):
        return [translate_schema(x, catalogue, source_route, field) for x in node]
    if isinstance(node, dict):
        result = {}
        for key, value in node.items():
            if key == 'inLanguage':
                result[key] = ['de', 'en'] if node.get('@type') == 'WebSite' else 'en'
            elif key == 'url' and node.get('@type') in ('Person', 'LocalBusiness', 'WebSite'):
                result[key] = value
            elif key in ('knowsLanguage', 'availableLanguage', 'address', 'sameAs', 'email', 'telephone'):
                result[key] = value
            else:
                result[key] = translate_schema(value, catalogue, source_route, key)
        return result
    if isinstance(node, str):
        if field in ('@id', 'url', 'item') and node.startswith(ORIGIN) and node not in SHARED_IDS:
            return english_url(node, source_route)
        if field in TEXT_FIELDS:
            return translate(node, catalogue)
    return node


def translate_js(source, catalogue):
    # Translate complete literal values only, never JavaScript identifiers.
    # These pages use plain quoted display strings, not interpolated templates.
    def literal(match):
        raw = match.group(0)
        value = raw[1:-1]
        if '\\' in value:
            return raw
        if value in ('de-DE', 'de_DE'):
            return json.dumps('en-GB' if value == 'de-DE' else 'en_GB')
        result = translate(value, catalogue)
        if raw.startswith('`') and result != value:
            return '`' + result.replace('`', '\\`') + '`'
        return json.dumps(result, ensure_ascii=False) if result != value else raw
    return re.sub(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`''', literal, source)


class EnglishHTML(HTMLParser):
    def __init__(self, source, catalogue, source_route):
        super().__init__(convert_charrefs=True)
        self.catalogue, self.source_route = catalogue, source_route
        self.out = []
        self.mode = None
        self.feed(source)

    def handle_decl(self, decl):
        self.out.append('<!' + decl + '>')

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        raw = self.get_starttag_text()
        changes = {}
        for key, value in pairs:
            if value is None:
                continue
            if key in ATTR_FIELDS:
                changes[key] = translate(value, self.catalogue)
            elif key == 'data-search':
                changes[key] = translate(value, self.catalogue, composite=True)
            elif key in ('href', 'src'):
                changes[key] = english_url(value, self.source_route)
            elif key.startswith(('x-', ':', '@')):
                changes[key] = translate_js(value, self.catalogue)
        if tag == 'html':
            changes['lang'] = 'en'
        if tag == 'meta':
            name = attrs.get('name', attrs.get('property'))
            if name in META_FIELDS:
                changes['content'] = translate(attrs.get('content', ''), self.catalogue)
            elif name == 'og:locale':
                changes['content'] = 'en_GB'
            elif name == 'og:url':
                changes['content'] = english_url(attrs['content'], self.source_route)
        def replace_attr(match):
            key, quote, value = match.group(1), match.group(2), match.group(3)
            if key.lower() not in changes:
                return match.group(0)
            return key + '=' + quote + escape(changes[key.lower()], quote=True) + quote
        raw = re.sub(r'([@\w:.-]+)\s*=\s*([\"\x27])(.*?)\2', replace_attr, raw, flags=re.S)
        self.out.append(raw)
        if tag in ('script', 'style'):
            self.mode = 'json' if attrs.get('type') == 'application/ld+json' else tag

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        self.out.append('</' + tag + '>')
        if tag in ('script', 'style'):
            self.mode = None

    def handle_data(self, data):
        if self.mode == 'json':
            graph = translate_schema(json.loads(data), self.catalogue, self.source_route)
            self.out.append(json.dumps(graph, ensure_ascii=False, separators=(',', ':')))
        elif self.mode:
            self.out.append(translate_js(data, self.catalogue) if self.mode == 'script' else data)
        else:
            self.out.append(escape(translate(data, self.catalogue), quote=False))

    def handle_comment(self, data):
        # Implementation comments are not published in the translated document.
        pass


def strip_language_links(source):
    source = re.sub(r'\n?<!-- locale-head -->.*?<!-- /locale-head -->\n?', '', source, flags=re.S)
    source = re.sub(r'\n?<!-- locale-nav -->.*?<!-- /locale-nav -->', '', source, flags=re.S)
    return re.sub(r'\n+(?=</head>)', '\n', source)


def add_language_links(source, source_route, language):
    source = strip_language_links(source)
    de, en = source_route, '/en' + source_route
    head = ('\n<!-- locale-head -->\n'
            f'<link rel="alternate" hreflang="de" href="{ORIGIN}{de}">\n'
            f'<link rel="alternate" hreflang="en" href="{ORIGIN}{en}">\n'
            '<link rel="stylesheet" href="/assets/locale.css">\n'
            f'<link rel="help" type="text/plain" href="{"/en" if language == "en" else ""}/llms.txt" title="{"Content guide" if language == "en" else "Inhaltsübersicht"}">\n'
            '<!-- /locale-head -->\n')
    source = source.replace('</head>', head + '</head>', 1)
    label = 'Sprache wählen' if language == 'de' else 'Choose language'
    links = ''.join(f'<a href="{url}" lang="{lang}" hreflang="{lang}"'
                    + (' aria-current="page"' if lang == language else '')
                    + f'>{lang.upper()}</a>' for lang, url in [('de', de), ('en', en)])
    nav = f'\n<!-- locale-nav --><nav class="language-switcher" aria-label="{label}">{links}</nav><!-- /locale-nav -->'
    if '</header>' in source:
        return source.replace('</header>', '</header>' + nav, 1)
    return source.replace('<body>', '<body>' + nav, 1)


class Markdown(HTMLParser):
    """Text counterpart with links/headings/lists; omit SVG/code and site chrome."""
    def __init__(self, source, base_url):
        super().__init__(convert_charrefs=True)
        self.out, self.anchors = [], []
        self.active = False
        self.hidden = 0
        self.base_url = base_url
        self.heading = False
        self.table_head = False
        self.feed(source)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag in ('main', 'footer'):
            self.active = True
        if tag in ('script', 'style', 'svg'):
            self.hidden += 1
        if not self.active or self.hidden:
            return
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.heading = True
            self.out.append('\n\n' + '#' * int(tag[1]) + ' ')
        elif tag in ('p', 'div', 'section', 'ul', 'ol', 'details', 'summary'):
            self.out.append('\n\n')
        elif tag == 'li':
            self.out.append('\n- ')
        elif tag == 'br':
            self.out.append(' ' if self.heading else '  \n')
        elif tag == 'table':
            self.out.append('\n\n')
        elif tag == 'tr':
            self.out.append('\n| ')
        elif tag == 'thead':
            self.table_head = True
        elif tag == 'img' and attrs.get('alt'):
            self.out.append(attrs['alt'])
        elif tag in ('strong', 'b'):
            self.out.append('**')
        elif tag in ('em', 'i'):
            self.out.append('*')
        elif tag == 'a':
            self.anchors.append(urljoin(self.base_url, attrs.get('href', '')))
            self.out.append('[')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'svg'):
            self.hidden -= 1
            return
        if not self.active or self.hidden:
            return
        if tag in ('strong', 'b'):
            self.out.append('**')
        elif tag in ('em', 'i'):
            self.out.append('*')
        elif tag == 'a' and self.anchors:
            self.out.append('](<' + self.anchors.pop() + '>)')
        elif tag in ('p', 'div', 'section', 'li', 'summary') or re.fullmatch('h[1-6]', tag):
            self.out.append('\n\n')
        elif tag == 'span':
            self.out.append(' ')
        elif tag in ('button', 'label', 'kbd'):
            self.out.append(' ')
        elif tag in ('th', 'td'):
            self.out.append(' | ')
        elif tag == 'tr':
            if self.table_head:
                row = ''.join(self.out).split('\n')[-1]
                self.out.append('\n|' + ' --- |' * (row.count('|') - 1))
            self.out.append('\n')
        elif tag == 'thead':
            self.table_head = False
        elif tag == 'table':
            self.out.append('\n\n')
        if re.fullmatch('h[1-6]', tag): self.heading = False
        if tag in ('main', 'footer'):
            self.active = False

    def handle_data(self, data):
        if self.active and not self.hidden:
            self.out.append(re.sub(r'\s+', ' ', data))

    def render(self):
        result = ''.join(self.out)
        result = re.sub(r'[ \t]+\n', '\n', result)
        result = re.sub(r'\n[ \t]+', '\n', result)
        result = re.sub(r'\[([^\[\]]*)\]\(<([^>]*)>\)', lambda m: '[' + ' '.join(m[1].split()) + '](<' + m[2] + '>)', result)
        return re.sub(r'\n{3,}', '\n\n', result).strip() + '\n'


def metadata(source):
    class Meta(HTMLParser):
        def __init__(self):
            super().__init__()
            self.title, self.description, self.in_title = '', '', False
        def handle_starttag(self, tag, pairs):
            attrs = dict(pairs)
            if tag == 'title': self.in_title = True
            if tag == 'meta' and attrs.get('name') == 'description': self.description = attrs['content']
        def handle_endtag(self, tag):
            if tag == 'title': self.in_title = False
        def handle_data(self, data):
            if self.in_title: self.title += data
    meta = Meta()
    meta.feed(source)
    return meta.title, meta.description


def build():
    mapping = []
    for path in pages():
        source_route = route(path)
        slug = path.parent.name if path.parent != ROOT else 'home'
        catalogue = load_catalogue(slug)
        source = path.read_text(encoding='utf-8')
        # Remove generated locale additions before translating, then reinsert once.
        clean = strip_language_links(source)
        english = ''.join(EnglishHTML(clean, catalogue, source_route).out)
        english = add_language_links(english, source_route, 'en')
        target = ROOT / 'en' / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(english, encoding='utf-8')
        title, description = metadata(english)
        front = '\n'.join(['---', 'title: ' + json.dumps(title, ensure_ascii=False),
                          'description: ' + json.dumps(description, ensure_ascii=False),
                          'url: ' + json.dumps(ORIGIN + '/en' + source_route), '---', ''])
        target.with_suffix('.md').write_text(front + '\n' + Markdown(english, ORIGIN + '/en' + source_route).render(), encoding='utf-8')
        path.write_text(add_language_links(clean, source_route, 'de'), encoding='utf-8')
        mapping.append({'de': source_route, 'en': '/en' + source_route})
    (CATALOGUES / 'routes.json').write_text(json.dumps(mapping, indent=2) + '\n', encoding='utf-8')
    icon_target = ROOT / 'en/assets/icons'
    icon_target.mkdir(parents=True, exist_ok=True)
    home = load_catalogue('home')
    for icon in (ROOT / 'assets/icons').glob('*.svg'):
        source = icon.read_text(encoding='utf-8')
        source = re.sub(r'(<title[^>]*>)(.*?)(</title>)', lambda m: m[1] + escape(translate(unescape(m[2]), home)) + m[3], source)
        (icon_target / icon.name).write_text(source, encoding='utf-8')
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    tree = sitemap.getroot()
    namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    ET.register_namespace('', namespace[1:-1])
    known = {node.text for node in tree.findall('.//' + namespace + 'loc')}
    for pair in mapping:
        url = ORIGIN + pair['en']
        if url not in known:
            node = ET.SubElement(tree, namespace + 'url')
            ET.SubElement(node, namespace + 'loc').text = url
    ET.indent(tree, space='  ')
    sitemap.write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (ROOT / 'links.txt').write_text(''.join(ORIGIN + pair[lang] + '\n' for lang in ('de', 'en') for pair in mapping), encoding='utf-8')
    print(f'Built {len(mapping)} English pages, Markdown counterparts and bilingual discovery files.')


if __name__ == '__main__':
    build()

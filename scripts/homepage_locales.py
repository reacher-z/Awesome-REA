"""Localize built homepage HTML from literal UI strings, without executing JavaScript."""
from html import escape
from html.parser import HTMLParser
import json
import re
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit

from open_graph import open_graph_meta
from build_survey import TITLES as SURVEY_TITLES
from contribution_pages import TITLES as CONTRIBUTION_TITLES

# Homepage ItemList names: each destination page's H1, not the arrowed link text.
HOMEPAGE_DESTINATIONS = {
    'browse': ('Browse repositories by category', '按分类浏览仓库'),
    'resources': ('Curated reverse engineering resources', '精选逆向工程资源'),
    'cases': ('Reverse-engineering case studies', '逆向工程案例合集'),
    'papers': ('Reverse engineering papers & benchmarks', '逆向工程论文与评测基准'),
    'survey': SURVEY_TITLES,
    'about': ('About the collection and its sources', '关于合集与数据来源'),
    'contribute': CONTRIBUTION_TITLES,
}


class _Strings:
    """A deliberately small parser: objects, quoted strings, comments, trailing commas."""
    def __init__(self, source, position):
        self.source, self.position = source, position

    def skip(self):
        while True:
            match = re.match(r'\s+|//[^\n]*(?:\n|$)|/\*[\s\S]*?\*/', self.source[self.position:])
            if not match:
                return
            self.position += len(match[0])

    def take(self, token):
        self.skip()
        if not self.source.startswith(token, self.position):
            raise ValueError('UI must contain only literal string dictionaries')
        self.position += len(token)

    def string(self):
        self.skip()
        quote = self.source[self.position:self.position + 1]
        if quote not in {'"', "'"}:
            raise ValueError('UI keys and values must be quoted string literals')
        self.position += 1
        result = []
        escapes = {'n': '\n', 'r': '\r', 't': '\t', 'b': '\b', 'f': '\f',
                   'v': '\v', '\\': '\\', '/': '/', '"': '"', "'": "'"}
        while self.position < len(self.source):
            char = self.source[self.position]; self.position += 1
            if char == quote:
                # Join a JS UTF-16 surrogate pair; reject lone surrogate escapes.
                return ''.join(result).encode('utf-16', 'surrogatepass').decode('utf-16')
            if char in '\r\n':
                raise ValueError('Unescaped newline in UI string')
            if char != '\\':
                result.append(char); continue
            char = self.source[self.position:self.position + 1]; self.position += 1
            if char in escapes:
                result.append(escapes[char])
            elif char in {'u', 'x'}:
                size = 4 if char == 'u' else 2
                digits = self.source[self.position:self.position + size]
                if len(digits) != size or not re.fullmatch(r'[0-9a-fA-F]+', digits):
                    raise ValueError('Unsupported UI string escape')
                result.append(chr(int(digits, 16))); self.position += size
            else:
                raise ValueError('Unsupported UI string escape')
        raise ValueError('Unterminated UI string')

    def object(self):
        self.take('{'); result = {}
        while True:
            self.skip()
            if self.source.startswith('}', self.position):
                self.position += 1; return result
            key = self.string(); self.take(':'); self.skip()
            if key in result:
                raise ValueError('Duplicate UI dictionary key')
            result[key] = self.object() if self.source.startswith('{', self.position) else self.string()
            self.skip()
            if self.source.startswith('}', self.position):
                self.position += 1; return result
            self.take(',')


def _ui_strings(source):
    declarations = list(re.finditer(r'(?m)^\s*const\s+UI\s*=\s*', source))
    if len(declarations) != 1:
        raise ValueError('Expected exactly one const UI dictionary')
    parser = _Strings(source, declarations[0].end())
    result = parser.object(); parser.take(';')
    if set(result) != {'en', 'zh'} or any(not isinstance(values, dict) or
            any(not isinstance(key, str) or not isinstance(value, str) for key, value in values.items())
            for values in result.values()):
        raise ValueError('Expected EN/ZH dictionaries of strings')
    return result


def _zh_repository_paths(source):
    """Repository documents with a Chinese counterpart, read from the literal app.js also uses."""
    declarations = list(re.finditer(r'(?m)^\s*const\s+ZH_REPOSITORY_PATHS\s*=\s*', source))
    if not declarations:
        return {}
    if len(declarations) != 1:
        raise ValueError('Expected at most one const ZH_REPOSITORY_PATHS dictionary')
    parser = _Strings(source, declarations[0].end())
    result = parser.object(); parser.take(';')
    if any(not isinstance(value, str) or not re.fullmatch(r'blob/main/[A-Za-z0-9._/-]+\.md', value)
           for item in result.items() for value in item):
        raise ValueError('Chinese repository paths must map Markdown files under blob/main/')
    return result


_VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class _Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source, self.nodes, self.stack = source, [], []
        self.lines = [0] + [match.end() for match in re.finditer('\n', source)]
        self.feed(source); self.close()

    def source_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def start(self, tag, attrs, closed):
        if len(dict(attrs)) != len(attrs):
            raise ValueError('Homepage markup must not contain duplicate attributes')
        node = {'tag': tag, 'attrs': dict(attrs), 'start': self.source_offset(),
                'inner': self.source_offset() + len(self.get_starttag_text()),
                'end': None, 'close': None, 'closed': closed, 'parent': self.stack[-1] if self.stack else None}
        self.nodes.append(node)
        if closed or tag in _VOID:
            node['close'] = node['end'] = node['inner']
        else:
            self.stack.append(node)

    def handle_starttag(self, tag, attrs):
        self.start(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self.start(tag, attrs, True)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1]['tag'] != tag:
            raise ValueError('Homepage markup must have balanced non-void elements')
        node = self.stack.pop(); node['close'] = self.source_offset()
        node['end'] = self.source.index('>', self.source_offset()) + 1


def _markup(value):
    """data-i18n uses innerHTML; allow only the small presentational vocabulary."""
    parsed = _Document(value)
    if parsed.stack:
        raise ValueError('Unbalanced translation markup')
    for node in parsed.nodes:
        if node['tag'] == 'a':
            attrs = node['attrs']
            href = attrs.get('href', '')
            if not isinstance(href, str):
                raise ValueError('Translation links need an internal href')
            decoded = unquote(href)
            if (set(attrs) - {'href', 'lang'} or not href.startswith('/') or decoded.startswith('//')
                    or re.search(r'[\\\x00-\x20]', decoded) or urlsplit(href).netloc
                    or attrs.get('lang', 'en') not in {'en', 'zh-CN'}):
                raise ValueError('Translation links must be safe internal paths')
            continue
        if node['tag'] not in {'br', 'span', 'strong', 'em', 'b', 'i'} or set(node['attrs']) - {'class', 'aria-hidden'}:
            raise ValueError('Unsupported markup in UI translation')
    return value


def _root_url(value):
    parsed = urlsplit(value)
    if not value or value.startswith(('#', '//', '/')) or parsed.scheme:
        return value
    return urljoin('/', value)


def _locale_url(value, origin, language):
    parsed = urlsplit(value)
    if parsed.scheme and (parsed.scheme + '://' + parsed.netloc) != origin:
        return value
    if value.startswith(('#', '//')):
        return value
    path = parsed.path
    if path.startswith('/zh/'):
        path = path[3:]
    if path == '/' or any(path == '/' + area + '/' or path.startswith('/' + area + '/')
                          for area in HOMEPAGE_DESTINATIONS):
        path = ('/zh' if language == 'zh' else '') + path
    return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))


def localized_homepage(html, app_source, language):
    """Return deterministic EN or ZH homepage HTML; input assets/JSON-LD are already built.

    `language` is 'en' or 'zh'. Missing translations and nonliteral UI values fail
    the build. Other scripts are preserved, and no JavaScript is evaluated.
    """
    if language not in {'en', 'zh'}:
        raise ValueError('Homepage language must be en or zh')
    strings = _ui_strings(app_source)[language]
    # The build localizes the English template; the inverse map keeps a Chinese page convertible back.
    repository_paths = _zh_repository_paths(app_source)
    if language == 'en':
        repository_paths = {chinese: english for english, chinese in repository_paths.items()}
    document = _Document(html)
    if document.stack:
        raise ValueError('Homepage markup has unclosed elements')
    canonical_nodes = [n for n in document.nodes if n['tag'] == 'link' and n['attrs'].get('rel') == 'canonical']
    if len(canonical_nodes) != 1:
        raise ValueError('Homepage needs exactly one canonical URL')
    canonical = urlsplit(canonical_nodes[0]['attrs'].get('href', ''))
    if (canonical.scheme != 'https' or not canonical.netloc or canonical.username or canonical.password
            or canonical.path not in {'/', '/zh/'} or canonical.query or canonical.fragment):
        raise ValueError('Homepage canonical must be a clean HTTPS root or Chinese home URL')
    origin = canonical.scheme + '://' + canonical.netloc
    home = origin + ('/zh/' if language == 'zh' else '/')
    locale = 'zh-CN' if language == 'zh' else 'en'
    edits = []
    heads = [n for n in document.nodes if n['tag'] == 'head']
    if len(heads) != 1:
        raise ValueError('Homepage needs one head element')
    alternates = '\n'.join(f'<link rel="alternate" hreflang="{lang}" href="{origin}{path}">'
                           for lang, path in [('en', '/'), ('zh-CN', '/zh/'), ('x-default', '/')]) + '\n'
    edits.append((heads[0]['close'], heads[0]['close'], alternates))

    def translated(key):
        if key not in strings:
            raise ValueError('Missing homepage translation: ' + key)
        return strings[key]

    def schema_page(value):
        if isinstance(value, list):
            return [schema_page(item) for item in value]
        if not isinstance(value, dict):
            return value
        kind = value.get('@type')
        if kind == 'WebSite' or (isinstance(kind, list) and 'WebSite' in kind):
            return value
        result = {key: schema_page(item) for key, item in value.items()}
        if kind == 'CollectionPage' or (isinstance(kind, list) and 'CollectionPage' in kind):
            result.update({'url': home, 'name': translated('pageTitle'),
                           'description': translated('pageDescription'), 'inLanguage': locale})
            if '@id' in result:
                result['@id'] = home + ('#' + urlsplit(result['@id']).fragment if '#' in result['@id'] else '')
            items = result.get('mainEntity', {}).get('itemListElement', []) if isinstance(result.get('mainEntity'), dict) else []
            for item in items:
                if isinstance(item, dict) and isinstance(item.get('url'), str):
                    parsed = urlsplit(item['url'])
                    if parsed.netloc and parsed.scheme + '://' + parsed.netloc != origin:
                        continue
                    path = parsed.path.removeprefix('/zh').strip('/')
                    item['url'] = _locale_url(item['url'], origin, language)
                    if path in HOMEPAGE_DESTINATIONS:
                        item['name'] = HOMEPAGE_DESTINATIONS[path][language == 'zh']
        return result

    # The template's social tags are replaced by the block every generator shares.
    social = [n for n in document.nodes if n['tag'] == 'meta' and (
        (n['attrs'].get('property') or '').startswith('og:') or (n['attrs'].get('name') or '').startswith('twitter:'))]
    images = [n['attrs'].get('content') for n in social if n['attrs'].get('property') == 'og:image']
    if len(images) != 1 or not images[0]:
        raise ValueError('Homepage needs exactly one og:image URL')

    def own_line(node):
        """Span a tag with its indentation and newline when it is alone on its line."""
        start = html.rfind('\n', 0, node['start']) + 1
        if html[start:node['start']].strip() or html[node['end']:node['end'] + 1] != '\n':
            return node['start'], node['end']
        return start, node['end'] + 1

    for node in document.nodes:
        tag, original = node['tag'], node['attrs']
        attrs = dict(original)
        if tag == 'link' and attrs.get('rel') == 'alternate' and 'hreflang' in attrs:
            end = node['end'] + int(html[node['end']:node['end'] + 1] == '\n')
            edits.append((node['start'], end, '')); continue
        if social and node is social[0]:
            edits.append((node['start'], node['end'], open_graph_meta(
                language=language, title=translated('pageTitle'), description=translated('pageDescription'),
                image_url=images[0], url=home))); continue
        if any(node is other for other in social):
            edits.append((*own_line(node), '')); continue
        if tag == 'html': attrs['lang'] = locale
        if node is canonical_nodes[0]: attrs['href'] = home
        if tag == 'title': edits.append((node['inner'], node['close'], escape(translated('pageTitle'))))
        if 'data-i18n' in attrs:
            edits.append((node['inner'], node['close'], _markup(translated(attrs['data-i18n']))))
        for marker, target in [('data-i18n-placeholder', 'placeholder'), ('data-i18n-aria', 'aria-label')]:
            if marker in attrs: attrs[target] = translated(attrs[marker])
        if tag == 'meta' and attrs.get('name') == 'description':
            attrs['content'] = translated('pageDescription')
        for key in ('src', 'href', 'poster'):
            if key in attrs and isinstance(attrs[key], str): attrs[key] = _root_url(attrs[key])
        if tag == 'a' and 'href' in attrs:
            attrs['href'] = _locale_url(attrs['href'], origin, language)
        if 'data-language-link' in attrs:
            # Each language link keeps its own homepage on both pages, so it works before JavaScript runs.
            link_language = attrs['data-language-link']
            if tag != 'a' or link_language not in {'en', 'zh'}:
                raise ValueError('Homepage language links must be en or zh anchors')
            attrs['href'] = '/zh/' if link_language == 'zh' else '/'
            attrs.pop('aria-current', None)
            if link_language == language: attrs['aria-current'] = 'true'
        if attrs.get('data-repo-path') in repository_paths:
            # Chinese pages link the Chinese document; app.js then keeps the localized data-repo-path.
            path, href = attrs['data-repo-path'], attrs.get('href', '')
            if not href.endswith('/' + path):
                raise ValueError('Homepage repository link does not end with its data-repo-path')
            attrs['href'] = href[:-len(path)] + repository_paths[path]
            attrs['data-repo-path'] = repository_paths[path]
        if 'data-locale-path' in attrs:
            path = attrs['data-locale-path']
            if not re.fullmatch(r'[a-z][a-z0-9-]*(?:/[a-z0-9-]+)*', path):
                raise ValueError('Invalid homepage locale path')
            old = urlsplit(attrs.get('href', ''))
            fragment = attrs.get('data-locale-fragment', old.fragment)
            attrs['href'] = urlunsplit(('', '', ('/zh' if language == 'zh' else '') + '/' + path + '/', old.query, fragment))
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            value = json.loads(html[node['inner']:node['close']])
            updated = schema_page(value)
            edits.append((node['inner'], node['close'], json.dumps(updated, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')))
        if attrs != original:
            attributes = ''.join(' ' + key + ('' if value is None else '="' + escape(value, quote=True) + '"') for key, value in attrs.items())
            edits.append((node['start'], node['inner'], '<' + tag + attributes + ('/>' if node['closed'] else '>')))
    # Parent innerHTML replacements intentionally subsume edits to old descendants.
    result, cursor = [], 0
    for start, end, replacement in sorted(edits, key=lambda item: (item[0], -item[1])):
        if start < cursor: continue
        result.extend((html[cursor:start], replacement)); cursor = end
    result.append(html[cursor:])
    return ''.join(result)

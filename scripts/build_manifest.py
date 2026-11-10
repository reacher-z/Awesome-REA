"""Record deterministic hashes of public deployment files, without environment data."""
from __future__ import annotations

import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit

MANIFEST_NAME = 'build-manifest.json'
HTML_NORMALIZATION = 'cloudflare-public-html-v5'
CONTROL_FILES = {'CNAME', '.nojekyll', '_headers', '_redirects'}
FONT_SUFFIXES = {'.woff', '.woff2', '.ttf', '.otf', '.eot'}
PRIVATE_NAMES = re.compile(r'(?i)^(?:\.env(?:\..*)?|credentials?(?:[.-].*)?|secrets?(?:[.-].*)?)$')
EMPTY_SCRIPT = re.compile(r'<script\b[^>]*>\s*</script>\s*', re.I)
EMAIL_ANCHOR = re.compile(r'<a\b[^>]*>\[email&#160;protected\]</a>')
EMAIL_SCRIPT = re.compile(r'<script\b[^>]*>\s*</script>', re.I)
# A star count as repository_stats.star_count() writes it. The production build reads the counts when it runs, so
# two builds of one commit can differ here and nowhere else, and a new star is no reason to notify search engines.
# Comments and raw-text elements match first and stay byte-sensitive, whatever they contain.
STAR_COUNT = re.compile(
    rb'<!--.*?(?:-->|\Z)'
    rb'|<(script|style|textarea|title|xmp|iframe|noembed|noframes|noscript)\b.*?(?:</\1\s*>|\Z)'
    rb'|(<span class="[a-z-]+" data-stars="[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+">)[0-9]+(?:\.[0-9]k)?(</span>)',
    re.I | re.S)


class _TagAttributes(HTMLParser):
    def __init__(self, tag):
        super().__init__()
        self.tag = tag
        self.attributes = []

    def handle_starttag(self, tag, attributes):
        if tag == self.tag:
            self.attributes = attributes


class _ElementSpans(HTMLParser):
    """Find real element spans without rewriting comments or embedded source text."""
    RAW_TEXT = {'script', 'style', 'textarea', 'title', 'xmp', 'iframe',
                'noembed', 'noframes', 'plaintext', 'noscript'}

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0]
        for match in re.finditer('\n', source):
            self.lines.append(match.end())
        self.blocked = None
        self.anchor = None
        self.spans = []

    def source_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if self.blocked:
            return
        if tag in self.RAW_TEXT:
            self.blocked = (tag, self.source_offset())
        elif tag == 'a':
            self.anchor = self.source_offset()

    def handle_startendtag(self, tag, attrs):
        # A trailing slash does not close non-void elements in HTML.
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        end = self.source.find('>', self.source_offset()) + 1
        if self.blocked:
            if tag == self.blocked[0] and tag != 'plaintext':
                if tag == 'script':
                    self.spans.append(('script', self.blocked[1], end))
                self.blocked = None
            return
        if tag == 'a' and self.anchor is not None:
            self.spans.append(('a', self.anchor, end))
            self.anchor = None


def without_star_counts(content: bytes) -> bytes:
    return STAR_COUNT.sub(lambda match: match[2] + match[3] if match[2] else match[0], content)


def normalized_html_bytes(content: bytes) -> bytes:
    """Reverse recognized Cloudflare analytics and public-email transformations and blank star counts.

    Page markup, text, structured data, asset revisions, and other scripts remain
    byte-sensitive. Unexpected attributes or inline code are never discarded.
    """
    text = content.decode('utf-8')
    # Every transformation below needs a data-cfemail, data-cfasync or data-cf-beacon attribute, whose name the
    # parser reads case-insensitively; a page without one has nothing to reverse but its star counts.
    if 'data-cf' not in text.lower():
        return without_star_counts(content)

    def restore_email(match):
        parser = _TagAttributes('a')
        parser.feed(match[0])
        attrs = dict(parser.attributes)
        if (len(attrs) != len(parser.attributes)
                or set(attrs) != {'href', 'class', 'data-cfemail'}
                or attrs['href'] != '/cdn-cgi/l/email-protection'
                or attrs['class'] != '__cf_email__'):
            return match[0]
        encoded = attrs['data-cfemail'] or ''
        if not re.fullmatch(r'(?:[a-fA-F0-9]{2}){4,320}', encoded):
            return match[0]
        data = bytes.fromhex(encoded)
        try:
            address = bytes(byte ^ data[0] for byte in data[1:]).decode('ascii')
        except UnicodeDecodeError:
            return match[0]
        # Cloudflare obfuscates any word@dotted.name, such as "openssl@1.1" in a requirement, not only addresses
        # with an alphabetic top-level domain; the restored text is escaped and still hash-sensitive.
        if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", address):
            return match[0]
        return escape(address, quote=True)

    def remove_email_decoder(match):
        parser = _TagAttributes('script')
        parser.feed(match[0])
        attrs = dict(parser.attributes)
        if (len(attrs) == len(parser.attributes)
                and set(attrs) == {'data-cfasync', 'src'}
                and attrs['data-cfasync'] == 'false'
                and re.fullmatch(r'/cdn-cgi/scripts/[a-f0-9]{8}/cloudflare-static/email-decode\.min\.js', attrs['src'] or '')):
            return ''
        return match[0]

    def remove_beacon(match):
        parser = _TagAttributes('script')
        parser.feed(match[0])
        attrs = dict(parser.attributes)
        allowed = {'src', 'defer', 'integrity', 'data-cf-beacon', 'crossorigin', 'type'}
        if len(attrs) != len(parser.attributes) or set(attrs) - allowed or 'data-cf-beacon' not in attrs:
            return match[0]
        if 'type' in attrs and attrs['type'] not in {'module', 'text/javascript', 'application/javascript'}:
            return match[0]
        source = urlsplit(attrs.get('src') or '')
        if (source.scheme == 'https' and source.netloc == 'static.cloudflareinsights.com'
                and (source.path == '/beacon.min.js' or source.path.startswith('/beacon.min.js/'))):
            return ''
        return match[0]

    parser = _ElementSpans(text)
    parser.feed(text)
    replacements = []
    for tag, start, end in parser.spans:
        original = text[start:end]
        if tag == 'a':
            match = EMAIL_ANCHOR.fullmatch(original)
            replacement = restore_email(match) if match else original
        else:
            match = EMAIL_SCRIPT.fullmatch(original)
            if not match:
                continue
            replacement = remove_email_decoder(match)
            if replacement == original:
                replacement = remove_beacon(match)
                if replacement == '':
                    # Match the analytics injection's trailing whitespace, as v2 did.
                    while end < len(text) and text[end].isspace():
                        end += 1
        if replacement != original:
            replacements.append((start, end, replacement))
    for start, end, replacement in reversed(replacements):
        text = text[:start] + replacement + text[end:]
    return without_star_counts(text.encode('utf-8'))


def html_digest(content: bytes) -> str:
    return hashlib.sha256(normalized_html_bytes(content)).hexdigest()


def collect_manifest(site_dir: Path) -> dict:
    """Hash deployable public output; reject private files before reading them."""
    root = Path(site_dir)
    if not root.is_dir():
        raise ValueError('Deployment output directory is missing; build the site first')
    files = {}
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root).as_posix()
        if relative == MANIFEST_NAME or relative in CONTROL_FILES:
            continue
        if path.is_symlink():
            raise ValueError('Deployment output must not contain symbolic links')
        if (any(part.startswith('.') or part in {'node_modules', '__pycache__'} for part in path.relative_to(root).parts)
                or PRIVATE_NAMES.fullmatch(path.name)
                or path.suffix.lower() in {'.pem', '.key', '.p12', '.pfx'}):
            raise ValueError('Private or development-only files must not be in deployment output')
        if not path.is_file() or path.suffix.lower() in FONT_SUFFIXES:
            continue
        content = path.read_bytes()
        html = path.suffix.lower() == '.html'
        hashed = without_star_counts(content) if html else content
        item = {'sha256': hashlib.sha256(hashed).hexdigest(), 'bytes': len(hashed)}
        if html:
            item['html_sha256'] = html_digest(content)
        files[relative] = item
    if 'index.html' not in files or 'sitemap.xml' not in files:
        raise ValueError('Deployment manifest requires a built homepage and sitemap')
    return {
        'schema_version': 1,
        'algorithm': 'sha256',
        'html_normalization': HTML_NORMALIZATION,
        'files': files,
    }


def manifest_bytes(manifest: dict) -> bytes:
    return (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def write_build_manifest(site_dir: Path) -> dict:
    """Call after the build has written all public pages, assets, and sitemap."""
    manifest = collect_manifest(site_dir)
    (Path(site_dir) / MANIFEST_NAME).write_bytes(manifest_bytes(manifest))
    return manifest


def read_build_manifest(site_dir: Path, *, verify_files: bool = True) -> dict:
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Build manifest contains duplicate JSON keys')
            result[key] = value
        return result

    try:
        manifest = json.loads((Path(site_dir) / MANIFEST_NAME).read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    except (OSError, json.JSONDecodeError):
        raise ValueError('Build manifest is missing or invalid; rebuild the site') from None
    if (not isinstance(manifest, dict) or set(manifest) != {'schema_version', 'algorithm', 'html_normalization', 'files'}
            or type(manifest.get('schema_version')) is not int or manifest.get('schema_version') != 1 or manifest.get('algorithm') != 'sha256'
            or manifest.get('html_normalization') != HTML_NORMALIZATION or not isinstance(manifest.get('files'), dict)):
        raise ValueError('Unsupported build manifest schema')
    for name, item in manifest['files'].items():
        path = PurePosixPath(name)
        if (not name or path.is_absolute() or '..' in path.parts or '\\' in name
                or not isinstance(item, dict) or set(item) != ({'sha256', 'bytes', 'html_sha256'} if path.suffix.lower() == '.html' else {'sha256', 'bytes'})
                or type(item.get('bytes')) is not int or item['bytes'] < 0
                or not isinstance(item.get('sha256'), str) or not re.fullmatch(r'[a-f0-9]{64}', item['sha256'])
                or ('html_sha256' in item and (not isinstance(item['html_sha256'], str) or not re.fullmatch(r'[a-f0-9]{64}', item['html_sha256'])))):
            raise ValueError('Invalid public file entry in build manifest')
    if verify_files and manifest != collect_manifest(site_dir):
        raise ValueError('Build manifest differs from local output; rebuild before publishing or submitting')
    return manifest

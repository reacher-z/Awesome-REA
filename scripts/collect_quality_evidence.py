#!/usr/bin/env python3
"""Collect public evidence for the catalog's software entries.

The quality scorer is deliberately split in two:

* this collector reads public primary sources and writes a dated, compact
  evidence snapshot (``data/quality-evidence.json``);
* ``scripts/quality_scoring.py`` turns that snapshot into checks and scores
  without touching the network.

Keeping collection separate makes a score reproducible from the committed
snapshot, and keeps an API failure from silently becoming a quality judgement.
The snapshot records source URLs, the reviewed ref, and SHA-256 hashes. It
never stores credentials, downloaded executables or full repository trees.

Usage:
    python3 scripts/collect_quality_evidence.py --all
    python3 scripts/collect_quality_evidence.py --entry woxi-case --refresh
    python3 scripts/collect_quality_evidence.py --all --offline

Safety:
  - Only public HTTPS sources are read; the token is sent only to api.github.com.
  - README and page text is bounded and treated as untrusted input.
  - Raw HTTP responses stay in the ignored ``.cache/quality-evidence`` directory.
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import datetime as dt
import hashlib
import html as html_module
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_FILES = ("rea-resources.json", "tool-resources.json")
OUTPUT_PATH = ROOT / "data" / "quality-evidence.json"
CACHE_DIR = Path(os.environ.get("QUALITY_CACHE_DIR", ROOT / ".cache" / "quality-evidence"))
HTTP_CACHE_DIR = CACHE_DIR / "http"
SPEC_VERSION = "quality-evidence-v1"
SOFTWARE_KINDS = {"case-study", "project", "tool", "integration"}
MAX_README_BYTES = 512 * 1024
MAX_PAGE_BYTES = 2 * 1024 * 1024
# A large repository tree (for example Ghidra) is legitimate API JSON, not a page.
MAX_API_BYTES = 32 * 1024 * 1024
MAX_WORKFLOW_FILES = 2
MAX_SNIPPET = 320
MAX_LIST = 40
API_ROOT = "https://api.github.com"
GITHUB_HOSTS = {"github.com", "www.github.com"}
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
API_USER_AGENT = "awesome-rea-quality-evidence"

# File and path vocabulary. Matching is case-insensitive unless a display name
# is kept, so a repository that spells "Tests" still counts.
TEST_PATH = re.compile(
    r"(^|/)(?:tests?|__tests__|testdata|fixtures?|golden|goldens)(/|$)"
    r"|(^|/)(?:test_[^/]+\.py|[^/]+_test\.(?:py|rs|go|java|cs|js|ts|rb|php|c|cpp))$"
    r"|\.(?:test|spec)\.[a-z0-9]+$",
    re.IGNORECASE,
)
SPEC_PATH = re.compile(r"(^|/)(?:specs?|requirements|design)(/|$)", re.IGNORECASE)
CI_PATH = re.compile(
    r"^\.github/workflows/[^/]+\.ya?ml$|^\.gitlab-ci\.ya?ml$|^azure-pipelines\.ya?ml$"
    r"|^\.circleci/config\.ya?ml$|^Jenkinsfile$|^\.travis\.ya?ml$|^appveyor\.ya?ml$",
    re.IGNORECASE,
)
DOC_PATH = re.compile(r"(^|/)(?:docs?|documentation|manual|guide|website)(/|$)|\.md$", re.IGNORECASE)
BENCHMARK_PATH = re.compile(
    r"(^|/)(?:bench|benches|benchmark|benchmarks|perf|performance|criterion)(/|$)"
    r"|(^|/)(?:benchmark|bench)[^/]*\.(?:py|rs|js|ts|go|java|c|cpp)$",
    re.IGNORECASE,
)
UI_TEST_PATH = re.compile(
    r"(^|/)(?:playwright|cypress|e2e|visual|screenshots?|storybook|\.storybook)(/|$)"
    r"|playwright\.config\.|cypress\.config\.|\.stories\.|\.story\.(?:js|jsx|ts|tsx)$",
    re.IGNORECASE,
)
SECURITY_PATH = re.compile(
    r"(^|/)(?:SECURITY\.md|\.gitleaks\.toml|\.snyk|security|threat-model|threat_model)(/|$)"
    r"|(^|/)\.github/(?:SECURITY\.md|dependabot\.ya?ml)$",
    re.IGNORECASE,
)
MIGRATION_PATH = re.compile(
    r"(^|/)(?:migrations?|migrate|alembic|prisma|schema)(/|$)|alembic\.ini$|schema\.prisma$",
    re.IGNORECASE,
)
DOCKER_PATH = re.compile(
    r"(^|/)(?:Dockerfile|Containerfile|docker-compose\.ya?ml|compose\.ya?ml|\.devcontainer)(/|$|\.)",
    re.IGNORECASE,
)
FIXTURE_PATH = re.compile(r"(^|/)(?:fixtures?|samples?|examples?|testdata|golden|goldens)(/|$)", re.IGNORECASE)

MANIFESTS = {
    "cargo.toml", "package.json", "pyproject.toml", "setup.py", "setup.cfg",
    "cmakelists.txt", "makefile", "gnumakefile", "go.mod", "build.gradle",
    "build.gradle.kts", "pom.xml", "gemfile", "composer.json", "meson.build",
    "configure.ac", "flake.nix", "default.nix", "dockerfile", "containerfile",
    "build.bazel", "workspace", "package.swift", "pubspec.yaml", "project.clj",
    "deps.edn", "mix.exs", "stack.yaml", "cabal.project",
}
MANIFEST_SUFFIXES = (".csproj", ".sln", ".vcxproj", ".fsproj", ".vbproj")
LOCKFILES = {
    "cargo.lock", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "poetry.lock", "uv.lock", "pipfile.lock", "go.sum", "gemfile.lock",
    "composer.lock", "packages.lock.json", "mix.lock", "pubspec.lock",
    "podfile.lock", "flake.lock", "bun.lock", "bun.lockb", "deno.lock",
}
LICENSE_PREFIXES = ("license", "licence", "copying", "notice", "unlicense")
SOURCE_EXTENSIONS = {
    ".py", ".rs", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".c", ".cc",
    ".cpp", ".h", ".hpp", ".go", ".java", ".kt", ".kts", ".cs", ".swift", ".m",
    ".mm", ".rb", ".php", ".lua", ".sh", ".zig", ".nim", ".ex", ".exs", ".clj",
    ".hs", ".ml", ".fs", ".vb", ".dart", ".sol", ".asm", ".s",
}
FORMAT_EXTENSIONS = {
    ".pdf", ".gltf", ".glb", ".obj", ".fbx", ".dae", ".stl", ".ply", ".3mf",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".psd", ".xcf", ".blend",
    ".doc", ".docx", ".odt", ".rtf", ".xls", ".xlsx", ".ods", ".csv", ".tsv",
    ".ppt", ".pptx", ".odp", ".wav", ".mp3", ".flac", ".ogg", ".mp4", ".webm",
    ".mov", ".mkv", ".zip", ".tar.gz", ".7z", ".iso", ".bin", ".elf", ".exe",
    ".dll", ".so", ".dylib", ".class", ".dex", ".apk", ".ipa", ".wasm", ".json",
    ".xml", ".yaml", ".yml", ".toml", ".ini", ".sql", ".db", ".sqlite",
}
README_MEDIA_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".apng", ".mp4", ".webm", ".mov")
MEDIA_EXCLUDES = re.compile(
    r"shields\.io|badge|travis|codecov|coveralls|circleci|workflows|logo|icon|banner|"
    r"sponsor|powered\s*by|qr\s*code|二维码|加群|discord|telegram|donate|patreon|"
    r"star[- ]history|progress|license|snyk|gitter|liberapay|opencollective|"
    r"buymeacoffee|img\.shields\.io",
    re.IGNORECASE,
)
VIDEO_HOSTS = ("youtube.com", "youtu.be", "vimeo.com", "bilibili.com", "b23.tv", "youku.com", "douyin.com")
MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
HTML_IMAGE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)
HTML_HREF = re.compile(r"<a\b[^>]*\bhref=[\"']([^\"']+)[\"'][^>]*>([\s\S]{0,300}?)</a>", re.IGNORECASE)
HTML_TAG = re.compile(r"<[^>]+>")
FENCED_CODE = re.compile(r"```[^\n]*\n(.*?)```|~~~[^\n]*\n(.*?)~~~", re.DOTALL)
ATX_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
SETEXT_UNDERLINE = re.compile(r"^(=+|-+)\s*$")
INSTALL_COMMAND = re.compile(
    r"^(?:npm\s+(?:i|install)|npx|bunx|bun\s+(?:add|install)|yarn\s+(?:add|dlx)|"
    r"pnpm\s+(?:add|dlx)|pip\s+install|pipx\s+install|uv\s+(?:tool\s+install|run)|"
    r"cargo\s+install|go\s+install|brew\s+install|gem\s+install|conda\s+install|"
    r"dotnet\s+tool\s+(?:install|update)|winget\s+install|scoop\s+install|choco\s+install|"
    r"luarocks\s+install|pacman\s+-S|apt(?:-get)?\s+install|docker\s+(?:run|pull)|"
    r"make|cmake|\./configure|gradle|mvn|flutter\s+build|swift\s+build)\b",
    re.IGNORECASE,
)
TEST_COMMAND = re.compile(
    r"\b(?:pytest|py\.test|python\s+-m\s+(?:pytest|unittest)|unittest|cargo\s+test|"
    r"npm\s+(?:run\s+)?test|yarn\s+(?:run\s+)?test|pnpm\s+(?:run\s+)?test|"
    r"go\s+test|ctest|make\s+test|dotnet\s+test|mvn\s+test|gradle(?:w)?\s+test|"
    r"rspec|phpunit|mix\s+test|swift\s+test|flutter\s+test)\b",
    re.IGNORECASE,
)

SECTION_PATTERNS = {
    "features": re.compile(r"features?|capabilities|what\s+works|highlights|functionality|功能|特性", re.I),
    "install": re.compile(r"install|installation|build|setup|getting\s+started|get\s+started|quick\s?start|"
                          r"download|prerequisit|requirement|compile|部署|安装|构建|下载|开始", re.I),
    "usage": re.compile(r"usage|use|example|how\s+to|run|command|cmd|cli|quick\s?start|示例|用法|使用|运行", re.I),
    "tests": re.compile(r"tests?|testing|verification|validate|validation|correctness|quality|回归|测试|验证", re.I),
    "performance": re.compile(r"performance|benchmark|speed|latency|throughput|profiling|profil|fps|性能|基准", re.I),
    "security": re.compile(r"security|authentication|authorization|permissions?|roles?|tenants?|secrets?|"
                           r"sandbox|安全|认证|授权|权限", re.I),
    "ui": re.compile(r"\bui\b|\bux\b|interface|screenshots?|demo|preview|design|accessibility|keyboard|"
                     r"界面|截图|演示|设计|可访问", re.I),
    "persistence": re.compile(r"persist|storage|database|backup|restore|recovery|migration|save|state|"
                              r"持久|存储|数据库|备份|恢复|迁移", re.I),
    "concurrency": re.compile(r"concurren|parallel|async|thread|race|lock|atomic|transaction|consistency|"
                              r"并发|并行|线程|竞争|事务|一致", re.I),
    "formats": re.compile(r"formats?|import|export|convert|compatibility|file\s+types?|round.?trip|"
                          r"格式|导入|导出|转换|兼容", re.I),
    "docs": re.compile(r"documentation|docs?|guide|manual|api|reference|文档|指南|手册", re.I),
    "license": re.compile(r"license|licence|copying|credits|许可|授权", re.I),
    "roadmap": re.compile(r"roadmap|todo|not\s+implemented|limitations?|known\s+issues|status|progress|"
                          r"planned|wip|路线图|限制|已知问题|进度", re.I),
}

KEYWORD_GROUPS = {
    "tests": re.compile(r"\b(?:test|tests|tested|testing|unit\s+test|integration\s+test|"
                        r"differential|reference\s+implementation|oracle|golden|fixture|"
                        r"fuzz|property[- ]based|hypothesis|regression|verification)\b", re.I),
    "performance": re.compile(r"\b(?:benchmark|performance|latency|throughput|fps|frame\s+time|"
                              r"profil(?:e|ing)|memory\s+usage|speed|optimiz)\b", re.I),
    "security": re.compile(r"\b(?:security|authentication|authorization|permission|role|tenant|"
                           r"secret|token|owasp|zap|sandbox|vulnerab)\b", re.I),
    "ui": re.compile(r"\b(?:screenshot|demo|preview|ui|ux|interface|accessibility|aria|keyboard|"
                     r"playwright|cypress|pixelmatch|visual\s+regression)\b", re.I),
    "persistence": re.compile(r"\b(?:persist|database|storage|backup|restore|recovery|migration|"
                              r"retry|idempotent|transaction|save\s+state|crash)\b", re.I),
    "concurrency": re.compile(r"\b(?:concurren|parallel|async|thread|race\s+condition|lock|atomic|"
                              r"transaction|consistency|eventual)\b", re.I),
    "formats": re.compile(r"\b(?:import|export|convert|file\s+format|round.?trip|compatib|interoperab|"
                          r"qpdf|gltf|pdfium|ffmpeg|imagemagick)\b", re.I),
    "reproducibility": re.compile(r"\b(?:install|build|compile|version|release|license|checksum|sha-?256|"
                                  r"signature|reproducib|deterministic|pin(?:ned)?)\b", re.I),
}


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def load_catalog(path: Path | None = None) -> list[dict]:
    records = []
    for filename in CATALOG_FILES:
        records.extend(json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")))
    return records


def software_records(records: list[dict]) -> list[dict]:
    return [record for record in records if record.get("kind") in SOFTWARE_KINDS]


def github_slug(url: str) -> str | None:
    parts = urllib.parse.urlsplit(url)
    if (parts.hostname or "").lower() not in GITHUB_HOSTS:
        return None
    path = [part for part in parts.path.split("/") if part]
    if len(path) < 2:
        return None
    owner, repo = path[0], path[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"{owner}/{repo}"


def pinned_ref(record: dict) -> str | None:
    """A commit named by a GitHub blob/tree evidence link, if one is present."""
    urls = [record.get("evidence_url") or ""] + list(record.get("additional_evidence_urls") or [])
    for url in urls:
        match = re.match(
            r"https://(?:www\.)?github\.com/[^/]+/[^/]+/(?:blob|tree)/([0-9a-f]{7,40})(?:/|$)",
            url, re.IGNORECASE,
        )
        if match:
            return match.group(1)
    return None


class RateLimiter:
    """Sleep before the shared API budget runs out instead of failing the run."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.remaining: int | None = None
        self.reset_at: float | None = None
        self.notice: str | None = None

    def observe(self, headers) -> None:
        remaining = headers.get("X-RateLimit-Remaining") or headers.get("x-ratelimit-remaining")
        reset = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
        with self.lock:
            if remaining is not None and remaining.isdigit():
                self.remaining = int(remaining)
            if reset is not None and reset.isdigit():
                self.reset_at = float(reset)

    def wait(self) -> None:
        with self.lock:
            remaining, reset_at = self.remaining, self.reset_at
        if remaining is not None and remaining < 50 and reset_at:
            delay = max(reset_at - time.time(), 0) + 2
            if delay > 0:
                with self.lock:
                    if self.notice != "waiting":
                        self.notice = "waiting"
                        print(f"\nGitHub API budget low; waiting {delay:.0f}s for reset", file=sys.stderr)
                time.sleep(min(delay, 900))
            with self.lock:
                self.notice = None
                self.remaining = None


class HttpClient:
    def __init__(self, token: str | None, *, offline: bool = False) -> None:
        self.token = token
        self.offline = offline
        self.rate = RateLimiter()
        self.cache_dir = HTTP_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.opener = urllib.request.build_opener(_AuthStrippingRedirect())

    def _cache_path(self, url: str) -> Path:
        return self.cache_dir / (hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json")

    def get(self, url: str, *, accept: str, page: bool = False,
            timeout: int = 30, attempts: int = 4) -> dict:
        """Return {status, body_text|json, headers, cached, error} for one URL."""
        cache_path = self._cache_path(url)
        if cache_path.is_file():
            try:
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                cached = None
            if cached is not None:
                cached["cached"] = True
                return cached
        if self.offline:
            return {"status": 0, "error": "missing from offline cache", "cached": False}
        host = (urllib.parse.urlsplit(url).hostname or "").lower()
        headers = {"User-Agent": BROWSER_USER_AGENT if page else API_USER_AGENT, "Accept": accept}
        if host == "api.github.com" and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        last_error = None
        for attempt in range(attempts):
            self.rate.wait()
            request = urllib.request.Request(url, headers=headers)
            try:
                with self.opener.open(request, timeout=timeout) as response:
                    # A page can keep a connection open without ending the body.
                    # Read in bounded chunks against a wall-clock deadline so one
                    # slow host cannot block the whole batch.
                    limit = MAX_PAGE_BYTES if page else MAX_API_BYTES
                    chunks: list[bytes] = []
                    total = 0
                    deadline = time.monotonic() + max(timeout * 2, 20)
                    while total <= limit:
                        chunk = response.read(64 * 1024)
                        if not chunk:
                            break
                        chunks.append(chunk)
                        total += len(chunk)
                        if time.monotonic() > deadline:
                            break
                    body = b"".join(chunks)
                    self.rate.observe(response.headers)
                    if len(body) > limit:
                        return {"status": response.status, "error": "response exceeds the size cap",
                                "headers": dict(response.headers), "cached": False}
                    result = {
                        "status": response.status,
                        "headers": {key: value for key, value in response.headers.items()
                                    if key.lower() in {"content-type", "x-ratelimit-remaining",
                                                       "x-ratelimit-reset", "retry-after"}},
                        "body_base64": base64.b64encode(body).decode("ascii"),
                        "cached": False,
                    }
                    cache_path.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
                    return result
            except urllib.error.HTTPError as error:
                self.rate.observe(error.headers)
                last_error = f"HTTP {error.code}"
                if error.code in {403, 429}:
                    retry_after = error.headers.get("Retry-After")
                    delay = int(retry_after) if retry_after and retry_after.isdigit() else 60
                    time.sleep(min(delay, 900) * (attempt + 1) / 2)
                    continue
                if error.code in {500, 502, 503, 504}:
                    time.sleep(2 ** attempt)
                    continue
                return {"status": error.code, "error": last_error, "cached": False}
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                last_error = str(error)
                time.sleep(2 ** attempt)
        return {"status": 0, "error": last_error or "request failed", "cached": False}


class _AuthStrippingRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward a token to a different origin after a redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None:
            old = urllib.parse.urlsplit(req.full_url)
            target = urllib.parse.urlsplit(newurl)
            if (old.scheme, old.hostname, old.port) != (target.scheme, target.hostname, target.port):
                for container in (redirected.headers, redirected.unredirected_hdrs):
                    container.pop("Authorization", None)
        return redirected


def body_bytes(response: dict) -> bytes:
    return base64.b64decode(response.get("body_base64") or "")


def body_json(response: dict) -> object | None:
    try:
        return json.loads(body_bytes(response).decode("utf-8", "replace"))
    except (ValueError, TypeError):
        return None


def fetch_text(client: HttpClient, url: str, accept: str, *, page: bool = False) -> tuple[str | None, dict]:
    response = client.get(url, accept=accept, page=page)
    if response.get("error"):
        return None, response
    text = body_bytes(response).decode("utf-8", "replace")
    if len(text) > MAX_README_BYTES:
        text = text[:MAX_README_BYTES]
        response = dict(response, truncated=True)
    return text, response


# ---------------------------------------------------------------------------
# README and page analysis
# ---------------------------------------------------------------------------

def strip_fenced_code(text: str) -> str:
    return FENCED_CODE.sub("\n", text)


def code_blocks(text: str) -> list[str]:
    blocks = []
    for match in FENCED_CODE.finditer(text):
        block = (match.group(1) or match.group(2) or "").strip()
        if block:
            blocks.append(block)
    return blocks


def markdown_headings(text: str) -> list[tuple[int, str]]:
    """ATX and setext headings outside fenced code blocks."""
    lines = strip_fenced_code(text).splitlines()
    headings: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = ATX_HEADING.match(line.strip())
        if match:
            headings.append((len(match.group(1)), match.group(2).strip()))
            continue
        if index + 1 < len(lines) and line.strip() and SETEXT_UNDERLINE.match(lines[index + 1].strip()):
            level = 1 if lines[index + 1].strip().startswith("=") else 2
            headings.append((level, line.strip()))
    return headings


def section_ranges(text: str) -> list[tuple[str, str, int]]:
    """(heading, body, level) for each markdown heading, in document order."""
    lines = strip_fenced_code(text).splitlines()
    heading_indexes = []
    for index, line in enumerate(lines):
        match = ATX_HEADING.match(line.strip())
        if match:
            heading_indexes.append((index, len(match.group(1)), match.group(2).strip()))
        elif index + 1 < len(lines) and line.strip() and SETEXT_UNDERLINE.match(lines[index + 1].strip()):
            level = 1 if lines[index + 1].strip().startswith("=") else 2
            heading_indexes.append((index, level, line.strip()))
    sections = []
    for position, (index, level, heading) in enumerate(heading_indexes):
        end = len(lines)
        for next_index, next_level, _ in heading_indexes[position + 1:]:
            if next_level <= level:
                end = next_index
                break
        body = "\n".join(lines[index + 1:end]).strip()
        sections.append((heading, body, level))
    return sections


def canonical_sections(headings: list[tuple[int, str]], sections: list[tuple[str, str, int]]) -> dict:
    found: dict[str, dict] = {}
    for heading, body, level in sections:
        for key, pattern in SECTION_PATTERNS.items():
            if pattern.search(heading):
                found.setdefault(key, {
                    "heading": heading[:120],
                    "level": level,
                    "snippet": collapse_whitespace(body)[:MAX_SNIPPET],
                    "bullets": len(re.findall(r"^\s*(?:[-*+]|\d+\.)\s+\S", body, re.MULTILINE)),
                })
                break
    return found


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def first_sentence(text: str, pattern: re.Pattern) -> str | None:
    for match in pattern.finditer(text):
        start = max(text.rfind(".", 0, match.start()), text.rfind("\n", 0, match.start()),
                    text.rfind("。", 0, match.start())) + 1
        end = min(
            [position for position in (text.find(".", match.end()), text.find("\n", match.end()),
                                       text.find("。", match.end())) if position != -1]
            + [match.end() + 160]
        )
        snippet = collapse_whitespace(text[start:end])
        if snippet:
            return snippet[:MAX_SNIPPET]
    return None


def media_urls(text: str) -> list[dict]:
    media = []
    seen = set()
    for alt, url in MARKDOWN_IMAGE.findall(text) + [(match, match) for match in HTML_IMAGE.findall(text)]:
        lower = url.lower().split("?")[0]
        if any(lower.endswith(ext) for ext in README_MEDIA_EXTENSIONS) and not MEDIA_EXCLUDES.search(url):
            if url not in seen:
                seen.add(url)
                media.append({"type": "image", "url": url, "alt": collapse_whitespace(alt)[:120]})
    for url, label in HTML_HREF.findall(text):
        if any(host in url.lower() for host in VIDEO_HOSTS):
            if url not in seen:
                seen.add(url)
                media.append({"type": "video", "url": url, "alt": collapse_whitespace(label)[:120]})
    for url in MARKDOWN_LINK.findall(text):
        link = url[1]
        if any(host in link.lower() for host in VIDEO_HOSTS) and link not in seen:
            seen.add(link)
            media.append({"type": "video", "url": link, "alt": collapse_whitespace(url[0])[:120]})
    return media[:MAX_LIST]


def readme_signals(text: str, headings: list[tuple[int, str]], sections: list[tuple[str, str, int]]) -> dict:
    body = strip_fenced_code(text)
    lower = body.lower()
    canonical = canonical_sections(headings, sections)
    blocks = code_blocks(text)
    commands = []
    for block in blocks:
        for line in block.splitlines():
            line = line.strip().lstrip("$ ").strip()
            if INSTALL_COMMAND.search(line):
                commands.append(line[:200])
    media = media_urls(text)
    links = [link for _, link in MARKDOWN_LINK.findall(text)] + [url for url, _ in HTML_HREF.findall(text)]
    docs_links = [link for link in links if re.search(r"(^|\.)(docs?|documentation|wiki)\.", link, re.I)]
    demo_links = [link for link in links if re.search(r"\b(demo|playable|live\s+preview|try\s+it\s+online)\b", link, re.I)]
    keyword = {key: bool(pattern.search(body)) for key, pattern in KEYWORD_GROUPS.items()}
    keyword_snippets = {key: first_sentence(body, pattern) for key, pattern in KEYWORD_GROUPS.items()}
    claims = {
        "not_implemented": bool(re.search(r"\b(?:not\s+(?:yet\s+)?implemented|unimplemented|missing|todo|planned|wip)\b", lower)),
        "partial": bool(re.search(r"\b(?:partial(?:ly)?|subset|early\s+stage|prototype|experimental|preview)\b", lower)),
        "supported": bool(re.search(r"\b(?:supports?|supported|works\s+with|compatible\s+with|features?)\b", lower)),
        "tests": keyword["tests"],
        "checksum": bool(re.search(r"\b(?:sha-?256|sha-?512|checksum|md5|signature|gpg)\b", lower)),
        "benchmark": keyword["performance"],
    }
    return {
        "sections": canonical,
        "heading_count": len(headings),
        "bullets": len(re.findall(r"^\s*(?:[-*+]|\d+\.)\s+\S", body, re.MULTILINE)),
        "code_blocks": min(len(blocks), 50),
        "install_commands": sorted(set(commands))[:10],
        "media": media,
        "media_count": len(media),
        "links": {"count": len(links), "docs": docs_links[:5], "demo": demo_links[:5]},
        "keywords": keyword,
        "keyword_snippets": keyword_snippets,
        "claims": claims,
        "lines": len(text.splitlines()),
    }


def readme_evidence(text: str) -> dict:
    headings = markdown_headings(text)
    sections = section_ranges(text)
    return {
        "sha256": sha256_text(text),
        "bytes": len(text.encode("utf-8")),
        "headings": [{"level": level, "text": heading[:120]} for level, heading in headings[:MAX_LIST]],
        "signals": readme_signals(text, headings, sections),
    }


def page_evidence(text: str) -> dict:
    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    description_match = re.search(
        r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"']([^\"']*)[\"']", text, re.I)
    headings = [(int(level), collapse_whitespace(html_module.unescape(re.sub(HTML_TAG, "", body))))
                for level, body in re.findall(r"<h([1-3])[^>]*>(.*?)</h\1>", text, re.I | re.S)]
    plain = html_module.unescape(re.sub(HTML_TAG, " ", re.sub(
        r"<(script|style)\b.*?</\1>", " ", text, flags=re.I | re.S)))
    plain = collapse_whitespace(plain)
    sections = [("", plain, 1)]
    signals = readme_signals(plain, headings, sections)
    return {
        "title": collapse_whitespace(html_module.unescape(re.sub(HTML_TAG, "", title_match.group(1)))) if title_match else None,
        "description": collapse_whitespace(description_match.group(1)) if description_match else None,
        "sha256": sha256_text(text),
        "bytes": len(text.encode("utf-8")),
        "headings": [{"level": level, "text": heading[:120]} for level, heading in headings[:MAX_LIST]],
        "signals": signals,
    }


# ---------------------------------------------------------------------------
# Repository inventory
# ---------------------------------------------------------------------------

def tree_inventory(paths: list[str]) -> dict:
    names = [path.rsplit("/", 1)[-1] for path in paths]
    lowered = [path.lower() for path in paths]
    licenses = sorted({name for name in names if name.lower().startswith(LICENSE_PREFIXES)})[:10]
    tests = sorted({path for path, low in zip(paths, lowered) if TEST_PATH.search(low)})[:MAX_LIST]
    spec_docs = sorted({path for path, low in zip(paths, lowered) if SPEC_PATH.search(low)})[:MAX_LIST]
    ci = sorted({path for path, low in zip(paths, lowered) if CI_PATH.search(low)})[:MAX_LIST]
    docs = sorted({path for path, low in zip(paths, lowered) if DOC_PATH.search(low)})[:MAX_LIST]
    benchmarks = sorted({path for path, low in zip(paths, lowered) if BENCHMARK_PATH.search(low)})[:MAX_LIST]
    ui_tests = sorted({path for path, low in zip(paths, lowered) if UI_TEST_PATH.search(low)})[:MAX_LIST]
    security = sorted({path for path, low in zip(paths, lowered) if SECURITY_PATH.search(low)})[:MAX_LIST]
    migrations = sorted({path for path, low in zip(paths, lowered) if MIGRATION_PATH.search(low)})[:MAX_LIST]
    docker = sorted({path for path, low in zip(paths, lowered) if DOCKER_PATH.search(low)})[:MAX_LIST]
    fixtures = sorted({path for path, low in zip(paths, lowered) if FIXTURE_PATH.search(low)})[:MAX_LIST]
    manifests = sorted({name for name in names
                        if name.lower() in MANIFESTS or name.lower().endswith(MANIFEST_SUFFIXES)})[:10]
    lockfiles = sorted({name for name in names if name.lower() in LOCKFILES})[:10]
    formats: dict[str, int] = {}
    for path in lowered:
        suffix = Path(path).suffix
        if suffix in FORMAT_EXTENSIONS:
            formats[suffix] = formats.get(suffix, 0) + 1
    return {
        "path_count": len(paths),
        "license": licenses,
        "tests": tests,
        "test_count": len(tests),
        "spec_docs": spec_docs,
        "ci": ci,
        "docs": docs,
        "doc_count": len(docs),
        "manifests": manifests,
        "lockfiles": lockfiles,
        "benchmarks": benchmarks,
        "ui_tests": ui_tests,
        "security": security,
        "migrations": migrations,
        "docker": docker,
        "fixtures": fixtures[:MAX_LIST],
        "formats": dict(sorted(formats.items())),
        "source_files": sum(1 for path in lowered if Path(path).suffix in SOURCE_EXTENSIONS),
        "workflow_paths": [path for path in paths if CI_PATH.search(path)][:MAX_WORKFLOW_FILES],
    }


def release_evidence(releases: list[dict]) -> dict:
    assets = []
    for release in releases[:20]:
        for asset in release.get("assets") or []:
            assets.append({
                "name": asset.get("name") or "",
                "size": asset.get("size"),
                "download_count": asset.get("download_count"),
                "tag": release.get("tag_name"),
            })
    tags = [release.get("tag_name") for release in releases if release.get("tag_name")]
    bodies = " ".join(release.get("body") or "" for release in releases[:5])
    asset_names = [asset["name"] for asset in assets]
    return {
        "count": len(releases),
        "latest_tag": tags[0] if tags else None,
        "latest_published_at": (releases[0] or {}).get("published_at") if releases else None,
        "assets": assets[:MAX_LIST],
        "asset_count": len(assets),
        "checksums": sorted({name for name in asset_names
                             if re.search(r"(?:sha\d*256|checksums?|\.sig$|\.asc$)", name, re.I)})[:10],
        "semver_tags": [tag for tag in tags if re.search(r"v?\d+\.\d+", tag)][:10],
        "body_claims": {
            "checksum": bool(re.search(r"\b(?:sha-?256|checksum|md5)\b", bodies, re.I)),
            "signature": bool(re.search(r"\b(?:signature|signed|gpg|cosign)\b", bodies, re.I)),
            "notes": bool(bodies.strip()),
        },
    }


def workflow_test_commands(client: HttpClient, slug: str, ref: str, paths: list[str]) -> list[dict]:
    excerpts = []
    for path in paths[:MAX_WORKFLOW_FILES]:
        url = f"{API_ROOT}/repos/{slug}/contents/{urllib.parse.quote(path)}?ref={urllib.parse.quote(ref)}"
        response = client.get(url, accept="application/vnd.github.raw")
        if response.get("error"):
            continue
        text = body_bytes(response).decode("utf-8", "replace")[:20000]
        commands = sorted({match.group(0)[:120] for match in TEST_COMMAND.finditer(text)})
        excerpts.append({"path": path, "test_commands": commands[:10],
                         "sha256": sha256_text(text)})
    return excerpts


def repo_evidence(client: HttpClient, slug: str, ref_hint: str | None, *, refresh: bool = False) -> dict:
    base = f"{API_ROOT}/repos/{slug}"
    repo_response = client.get(base, accept="application/vnd.github+json")
    repo = body_json(repo_response)
    observed_at = now_utc()
    result = {
        "slug": slug,
        "url": f"https://github.com/{slug}",
        "observed_at": observed_at,
        "status": "observed",
        "ref": None,
        "pinned": bool(ref_hint),
        "repository": {},
        "readme": None,
        "tree": None,
        "releases": None,
        "workflows": [],
    }
    if not isinstance(repo, dict) or repo_response.get("error"):
        result["status"] = "unreachable"
        result["error"] = (repo_response.get("error") or "repository metadata unavailable")[:200]
        return result
    branch = repo.get("default_branch") or "main"
    ref = ref_hint or branch
    result["ref"] = ref
    result["repository"] = {
        "default_branch": branch,
        "archived": bool(repo.get("archived")),
        "disabled": bool(repo.get("disabled")),
        "fork": bool(repo.get("fork")),
        "created_at": repo.get("created_at"),
        "pushed_at": repo.get("pushed_at"),
        "updated_at": repo.get("updated_at"),
        "stars": repo.get("stargazers_count"),
        "forks": repo.get("forks_count"),
        "open_issues": repo.get("open_issues_count"),
        "topics": (repo.get("topics") or [])[:30],
        "language": repo.get("language"),
        "homepage": repo.get("homepage") or None,
        "description": repo.get("description") or None,
        "license": (repo.get("license") or {}).get("spdx_id"),
        "size_kb": repo.get("size"),
    }
    def fetch_readme(ref_value: str) -> tuple[str | None, str | None]:
        readme_url = f"{base}/readme?ref={urllib.parse.quote(ref_value)}"
        readme_response = client.get(readme_url, accept="application/vnd.github+json")
        readme_document = body_json(readme_response)
        text = None
        path = None
        if isinstance(readme_document, dict) and readme_document.get("content"):
            try:
                text = base64.b64decode(readme_document["content"]).decode("utf-8", "replace")
                path = readme_document.get("path")
            except (ValueError, KeyError):
                text = None
        if text is None and isinstance(readme_document, dict) and readme_document.get("path"):
            # A different URL keeps the JSON and raw representations from sharing
            # one cache entry; the readme endpoint itself may have answered JSON.
            contents_url = (f"{base}/contents/{urllib.parse.quote(readme_document['path'])}"
                            f"?ref={urllib.parse.quote(ref_value)}")
            text, _ = fetch_text(client, contents_url, "application/vnd.github.raw")
            path = readme_document.get("path")
        return text, path

    readme_text, readme_path = fetch_readme(ref)
    if readme_text is None and ref != branch:
        # A pinned evidence commit can disappear after a force-push or repository
        # transfer. Fall back to the default branch and record the actual ref.
        ref = branch
        result["ref"] = ref
        result["pinned"] = False
        readme_text, readme_path = fetch_readme(ref)
    if readme_text is not None:
        if len(readme_text.encode("utf-8")) > MAX_README_BYTES:
            readme_text = readme_text.encode("utf-8")[:MAX_README_BYTES].decode("utf-8", "ignore")
        result["readme"] = {"path": readme_path, "ref": ref, **readme_evidence(readme_text)}

    def fetch_tree(ref_value: str) -> dict | None:
        tree_url = f"{base}/git/trees/{urllib.parse.quote(ref_value)}?recursive=1"
        response = client.get(tree_url, accept="application/vnd.github+json")
        document = body_json(response)
        if isinstance(document, dict) and isinstance(document.get("tree"), list):
            return document
        return None

    tree = fetch_tree(ref)
    if tree is None and ref != branch:
        ref = branch
        result["ref"] = ref
        result["pinned"] = False
        tree = fetch_tree(ref)
    if tree is not None:
        paths = [item.get("path", "") for item in tree["tree"] if item.get("path")]
        result["tree"] = {
            "sha": tree.get("sha"),
            "truncated": bool(tree.get("truncated")),
            **tree_inventory(paths),
        }
        result["workflows"] = workflow_test_commands(
            client, slug, ref, result["tree"].get("workflow_paths") or [])
    releases_response = client.get(f"{base}/releases?per_page=100", accept="application/vnd.github+json")
    releases = body_json(releases_response)
    if isinstance(releases, list):
        result["releases"] = release_evidence(releases)
    return result


def page_evidence_for(client: HttpClient, url: str) -> dict:
    response = client.get(url, accept="text/html,application/xhtml+xml", page=True,
                          timeout=15, attempts=2)
    observed_at = now_utc()
    if response.get("error"):
        return {"url": url, "observed_at": observed_at, "status": "unreachable",
                "error": (response.get("error") or "page unavailable")[:200]}
    text = body_bytes(response).decode("utf-8", "replace")
    return {"url": url, "observed_at": observed_at, "status": "observed", **page_evidence(text)}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def build_document(entries: list[dict], client: HttpClient, *, workers: int) -> dict:
    github_entries = [entry for entry in entries if github_slug(entry["url"])]
    page_entries = [entry for entry in entries if not github_slug(entry["url"])]
    repos: dict[str, dict] = {}
    pages: dict[str, dict] = {}
    errors: list[dict] = []

    def fetch_repo(slug: str, ref: str | None) -> dict:
        return repo_evidence(client, slug, ref)

    # One request per repository; several catalog entries can point at the same one.
    wanted: dict[str, str | None] = {}
    for entry in github_entries:
        slug = github_slug(entry["url"])
        wanted.setdefault(slug, pinned_ref(entry))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch_repo, slug, ref): slug for slug, ref in wanted.items()}
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            slug = futures[future]
            try:
                result = future.result()
            except Exception as error:  # A single repository must not stop the batch.
                result = {"slug": slug, "url": f"https://github.com/{slug}", "status": "error",
                          "observed_at": now_utc(), "error": str(error)[:200]}
            repos[slug] = result
            if result.get("status") != "observed":
                errors.append({"source": "github", "slug": slug, "error": result.get("error")})
            print(f"\rcollected {index}/{len(wanted)} repositories", end="", file=sys.stderr)
    print(file=sys.stderr)

    def fetch_page(entry: dict) -> tuple[str, dict]:
        return entry["id"], page_evidence_for(client, entry["url"])

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(workers, 4)) as pool:
        futures = {pool.submit(fetch_page, entry): entry["id"] for entry in page_entries}
        for future in concurrent.futures.as_completed(futures):
            entry_id = futures[future]
            try:
                _, result = future.result()
            except Exception as error:
                result = {"status": "error", "error": str(error)[:200], "observed_at": now_utc()}
            pages[entry_id] = result
            if result.get("status") != "observed":
                errors.append({"source": "page", "entry": entry_id, "error": result.get("error")})

    entry_index = {}
    for entry in entries:
        slug = github_slug(entry["url"])
        entry_index[entry["id"]] = {
            "id": entry["id"],
            "name": entry.get("name"),
            "url": entry["url"],
            "kind": entry.get("kind"),
            "targets": entry.get("targets") or [],
            "source": "github" if slug else "page",
            "repo": slug,
            "page": None if slug else entry["id"],
        }
    observed_repos = sum(1 for result in repos.values() if result.get("status") == "observed")
    observed_pages = sum(1 for result in pages.values() if result.get("status") == "observed")
    return {
        "schema_version": 1,
        "meta": {
            "spec": SPEC_VERSION,
            "generated_at": now_utc(),
            "method": "Public GitHub REST metadata, README and tree, release assets and up to two CI workflow files; "
                      "non-GitHub entries read the public page. No executable is downloaded or run.",
            "entry_count": len(entries),
            "github_entry_count": len(github_entries),
            "page_entry_count": len(page_entries),
            "repository_count": len(repos),
            "repository_observed": observed_repos,
            "page_observed": observed_pages,
            "errors": errors[:100],
            "limits": [
                "The snapshot records public evidence, not runtime behaviour or product quality.",
                "A README keyword or a test directory does not prove that a feature works or that tests pass.",
                "GitHub metadata reflects the default branch or the evidence link's commit at collection time.",
                "Large repositories can return a truncated tree; the scorer treats missing paths as absent evidence.",
            ],
        },
        "repos": dict(sorted(repos.items())),
        "pages": dict(sorted(pages.items())),
        "entries": dict(sorted(entry_index.items())),
    }


def sanitize_private_text(value: str) -> str:
    """Replace local-profile paths and credential-looking text in a public snippet."""
    try:
        from review_pr import LOCAL_PATH, SENSITIVE
    except ImportError:
        return value
    return SENSITIVE.sub("<secret>", LOCAL_PATH.sub("<local-path>", value))


def sanitize_document(value):
    if isinstance(value, str):
        return sanitize_private_text(value)
    if isinstance(value, list):
        return [sanitize_document(item) for item in value]
    if isinstance(value, dict):
        return {sanitize_private_text(key): sanitize_document(item) for key, item in value.items()}
    return value


def trim_document(document: dict) -> dict:
    """Keep the committed snapshot reviewable without losing any field the scorer reads."""
    def trim_signals(signals: dict) -> None:
        if isinstance(signals.get("media"), list):
            signals["media"] = signals["media"][:5]
        if isinstance(signals.get("install_commands"), list):
            signals["install_commands"] = signals["install_commands"][:5]
        if isinstance(signals.get("keyword_snippets"), dict):
            signals["keyword_snippets"] = {
                key: (value[:200] if isinstance(value, str) else value)
                for key, value in signals["keyword_snippets"].items()
            }
        if isinstance(signals.get("sections"), dict):
            for payload in signals["sections"].values():
                if isinstance(payload, dict) and isinstance(payload.get("snippet"), str):
                    payload["snippet"] = payload["snippet"][:240]
        links = signals.get("links")
        if isinstance(links, dict):
            for key in ("docs", "demo"):
                if isinstance(links.get(key), list):
                    links[key] = links[key][:5]

    for repo in (document.get("repos") or {}).values():
        readme = repo.get("readme")
        if readme:
            readme.pop("headings", None)
            trim_signals(readme.get("signals") or {})
        inventory = repo.get("tree")
        if inventory:
            for key in ("tests", "spec_docs", "ci", "docs", "benchmarks", "ui_tests",
                        "security", "migrations", "docker", "fixtures"):
                if isinstance(inventory.get(key), list):
                    inventory[key] = inventory[key][:10]
            if isinstance(inventory.get("formats"), dict):
                inventory["formats"] = dict(list(inventory["formats"].items())[:8])
        releases = repo.get("releases")
        if releases and isinstance(releases.get("assets"), list):
            releases["assets"] = releases["assets"][:5]
        repository = repo.get("repository") or {}
        if isinstance(repository.get("topics"), list):
            repository["topics"] = repository["topics"][:10]
    for page in (document.get("pages") or {}).values():
        page.pop("headings", None)
        trim_signals(page.get("signals") or {})
    return sanitize_document(document)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry", action="append", help="Catalog entry ID; repeatable")
    parser.add_argument("--all", action="store_true", help="Every software entry in the catalog")
    parser.add_argument("--limit", type=int, help="Only the first N entries; useful for a smoke run")
    parser.add_argument("--refresh", action="store_true", help="Ignore the HTTP cache for this run")
    parser.add_argument("--offline", action="store_true", help="Read only the existing HTTP cache")
    parser.add_argument("--workers", type=int, default=6, help="Concurrent HTTP requests (default 6)")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    if not args.entry and not args.all:
        parser.error("choose --entry ID or --all")
    if args.refresh and args.offline:
        parser.error("--refresh and --offline cannot be combined")

    records = software_records(load_catalog())
    by_id = {record["id"]: record for record in records}
    if args.entry:
        missing = [entry_id for entry_id in args.entry if entry_id not in by_id]
        if missing:
            parser.error("unknown software entry ID(s): " + ", ".join(missing))
        selected = [by_id[entry_id] for entry_id in args.entry]
    else:
        selected = records
    if args.limit is not None:
        selected = selected[:args.limit]
    if args.refresh:
        # The HTTP client caches by URL; clearing the directory is the least
        # surprising way to honour --refresh without a second code path.
        for path in HTTP_CACHE_DIR.glob("*.json"):
            path.unlink()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        try:
            token = subprocess_token()
        except OSError:
            token = None
    client = HttpClient(token, offline=args.offline)
    document = trim_document(build_document(selected, client, workers=max(1, args.workers)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(f"wrote {len(document['entries'])} entries, {len(document['repos'])} repositories and "
          f"{len(document['pages'])} pages to {args.output}")
    if document["meta"]["errors"]:
        print(f"{len(document['meta']['errors'])} source(s) failed; see meta.errors", file=sys.stderr)
    return 0


def subprocess_token() -> str | None:
    """Use the local gh login when the environment has no token."""
    import subprocess
    result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True,
                            encoding="utf-8", timeout=10)
    return result.stdout.strip() or None


if __name__ == "__main__":
    raise SystemExit(main())

"""Followed-source leads: identities, source parsers, scope rules, selection, batch validation and review."""
from copy import deepcopy
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import build_discovery_leads
import collect_discovery_leads as collect
import discovery_leads as leads
import review_pr
from test_review_pr import NUMBER, FakeGitHub, run_review

NOW = '2026-11-05T21:00:00Z'
COMMIT = '1' * 40
PROVENANCE = {'repository': leads.REPOSITORY, 'workflow_path': leads.WORKFLOW_PATH, 'run_id': 42100000001,
              'run_attempt': 1, 'event': 'schedule', 'head_sha': 'a' * 40, 'registry_sha256': 'b' * 64}

LIST_README = '''# Awesome Example RE

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

## Contents

- [Tools](#tools)

## Tools

### Disassemblers

- [Toy Disassembler](https://github.com/toy-owner/toy-disasm) - Disassembles toy binaries. [Paper](https://arxiv.org/abs/2401.00001)
- [Second Tool](https://github.com/second/tool/tree/main/src) - A second tool.
- [Self](https://github.com/example/awesome-example-re) - the list itself.
- [Scanner](https://github.com/vendor/av-scanner) - An antivirus scanner.
- [Old Site](https://web.archive.org/web/2009/http://old.example.org/tool/) - Archived home page.
- ~~[Dead Tool](https://github.com/dead/tool)~~ - No longer maintained.

### Books

- [Practical Example Reversing](https://nostarch.com/practical-reversing) - A book.

## Community

- [Forum](https://forum.example.org/) - Talk about RE.

```
- [Code](https://github.com/in/code-block)
```
'''

SCOPE = {'include_sections': 'Tools', 'exclude_sections': 'Community', 'kind_rules': [['Books', 'learning-resource']],
         'rules': [{'pattern': r'^gh:vendor/av-scanner$', 'reason': 'detection-only'}]}


def repository_node(name, number, **changes):
    node = {'databaseId': number, 'nameWithOwner': name, 'isPrivate': False, 'isFork': False, 'isArchived': False,
            'stargazerCount': 10, 'pushedAt': '2026-10-01T00:00:00Z', 'description': f'{name} description',
            'homepageUrl': None, 'licenseInfo': {'spdxId': 'MIT'}, 'parent': None,
            'repositoryTopics': {'nodes': [{'topic': {'name': 'reverse-engineering'}}]}}
    node.update(changes)
    return node


def listing(source_id, url, key, *, label='Tool', section='Tools', kind='tool', **extra):
    return {'source_id': source_id, 'url': url, 'key': key, 'flags': {}, 'kind': kind, 'label': label,
            'section': section, 'evidence_url': f'https://github.com/example/list/blob/{COMMIT}/README.md#L1', **extra}


def github_lead(number, name=None, *, source='example-list'):
    name = name or f'owner{number}/tool{number}'
    candidates, _ = collect.candidates_from([listing(source, f'https://github.com/{name}', 'gh:' + name.lower())],
                                            {name.lower(): repository_node(name, number)}, NOW)
    return candidates[0]


def web_lead(url, *, source='example-list', kind='learning-resource'):
    key, _, flags = leads.url_key(url)
    candidates, _ = collect.candidates_from([{**listing(source, url, key, kind=kind), 'flags': flags}], {}, NOW)
    return candidates[0]


def source_results(*identifiers):
    return [collect.source_result({'id': identifier, 'type': 'github-readme-list'}, 'captured',
                                  {'links': 3, 'in_scope': 2},
                                  {'evidence_url': f'https://github.com/example/list/blob/{COMMIT}/README.md',
                                   'revision': COMMIT, 'content_sha256': 'c' * 64}) for identifier in identifiers]


def make_batch(candidates, *, existing=None, run_id=42100000001, sources=('example-list',), collected_at=NOW):
    provenance = {**PROVENANCE, 'run_id': run_id}
    existing = existing or {'known': {}, 'records': 0, 'bytes': 0}
    batch, status = leads.build_batch(candidates, source_results(*sources), provenance, existing,
                                      collected_at=collected_at, source_order=list(sources))
    assert status == 'selected', status
    return batch


def registry(**changes):
    document = {'schema_version': 1, 'kind': leads.REGISTRY_KIND, 'description': 'Test registry.',
                'exclusion_sets': {'shared': [{'pattern': '^gh:spam/', 'reason': 'unrelated'}]},
                'sources': [{'id': 'example-list', 'type': 'github-readme-list', 'repository': 'example/awesome-example-re',
                             'path': 'README.md', 'why': 'A test list.',
                             'scope': {'include_sections': 'Tools', 'exclusion_sets': ['shared']}}]}
    document.update(changes)
    return document


class IdentityTest(unittest.TestCase):
    def test_url_keys_follow_the_coverage_identity_rules(self):
        cases = {
            'https://github.com/Foo/Bar/tree/main/x': 'gh:foo/bar',
            'https://github.com/Foo': 'ghorg:foo',
            'https://github.com/topics/ida': None,
            'https://arxiv.org/pdf/2401.00001v3': 'arxiv:2401.00001',
            'https://doi.org/10.1145/ABC.123': 'doi:10.1145/abc.123',
            'https://dl.acm.org/doi/10.1145/3414173': 'doi:10.1145/3414173',
            'https://youtu.be/abc123': 'yt:abc123',
            'https://www.youtube.com/@channel': None,
            'https://web.archive.org/web/2009/http://Old.Example.org/tool/index.html': 'url:old.example.org/tool',
            'https://huggingface.co/datasets/LLM4Binary/decompile-bench': 'huggingface:dataset/LLM4Binary/decompile-bench',
            'https://huggingface.co/LLM4Binary/llm4decompile-1.3b': 'huggingface:model/LLM4Binary/llm4decompile-1.3b',
            'https://img.shields.io/badge/x': None,
            'https://example.github.io/Hardware%20Hacking/Notes': 'url:example.github.io/hardware%20hacking/notes',
            'https://twitter.com/someone': None,
        }
        for url, expected in cases.items():
            with self.subTest(url):
                self.assertEqual(leads.url_key(url)[0], expected)
        self.assertEqual(leads.url_key('https://owner.github.io/project/')[2]['ghpages_alias'], 'gh:owner/project')
        self.assertEqual(leads.title_key('SoK: AI-Augmented Binary Reversing'), 'title:sokaiaugmentedbinaryreversing')
        self.assertIsNone(leads.title_key('Short'))
        self.assertEqual(leads.lead_id('github:1'), 'lead-' + hashlib.sha256(b'github:1').hexdigest()[:24])


class RegistryTest(unittest.TestCase):
    def test_a_valid_registry_and_each_kind_of_mistake(self):
        self.assertEqual(leads.validate_registry(registry()), [])
        bad = registry()
        bad['sources'].append(deepcopy(bad['sources'][0]))
        self.assertIn('distinct', ' '.join(leads.validate_registry(bad)))
        for change, message in (({'type': 'ftp-list'}, 'unknown source type'),
                                ({'scope': {'include_sections': '('}}, 'invalid regular expression'),
                                ({'scope': {'exclude': [{'pattern': 'x', 'reason': 'boring'}]}}, 'known reason'),
                                ({'scope': {'exclusion_sets': ['missing']}}, 'registered exclusion sets'),
                                ({'path': '../README.md'}, 'relative repository path'),
                                ({'every_hours': 5}, 'every_hours'),
                                ({'extra': 1}, 'expected the github-readme-list fields')):
            document = registry()
            document['sources'][0].update(change)
            with self.subTest(change):
                self.assertIn(message, ' '.join(leads.validate_registry(document)))
        survey = registry()
        survey['sources'] = [{'id': 'survey-x', 'type': 'survey-references', 'paper_id': 'paper-missing', 'why': 'A survey.'}]
        self.assertIn('curated paper', ' '.join(leads.validate_registry(survey, [{'id': 'paper-other', 'arxiv_id': '2401.1'}])))

    def test_the_committed_registry_is_valid_and_a_missing_one_is_a_problem(self):
        document, problems = leads.load_registry(ROOT)
        self.assertEqual(problems, [])
        self.assertEqual(len({source['id'] for source in document['sources']}), len(document['sources']))
        types = {source['type'] for source in document['sources']}
        self.assertEqual(types, set(leads.SOURCE_TYPES))
        with tempfile.TemporaryDirectory() as directory:
            self.assertIn('is missing', ' '.join(leads.load_registry(Path(directory))[1]))


class ReadmeParserTest(unittest.TestCase):
    def test_sections_one_item_per_line_kinds_and_exclusions(self):
        source = {'id': 'example-list', 'repository': 'example/awesome-example-re', 'path': 'README.md', 'scope': SCOPE}
        found, counts = collect.readme_listings(source, LIST_README, COMMIT)
        self.assertEqual([row['key'] for row in found],
                         ['gh:toy-owner/toy-disasm', 'gh:second/tool', 'url:old.example.org/tool', 'url:nostarch.com/practical-reversing'])
        self.assertEqual((counts['excluded:detection-only'], counts['excluded:defunct']), (1, 1))
        first = found[0]
        self.assertEqual((first['label'], first['section'], first['kind']), ('Toy Disassembler', 'Tools > Disassemblers', 'tool'))
        self.assertEqual(first['evidence_url'], f'https://github.com/example/awesome-example-re/blob/{COMMIT}/README.md#L13')
        self.assertEqual(found[3]['kind'], 'learning-resource')
        self.assertNotIn('gh:in/code-block', [row['key'] for row in found])

    def test_quote_subsections_and_section_rules(self):
        text = '# List\n\n## RE\n\n> IDA Plugins\n- [A](https://github.com/a/a)\n\n> Guide\n- [B](https://github.com/b/b)\n'
        source = {'id': 'x', 'repository': 'x/x', 'path': 'README.md',
                  'scope': {'include_sections': '.', 'include_subsections': '^(IDA Plugins|Guide)$',
                            'rules': [{'pattern': r'^section:(?!Cheat > Guide$).*Guide$', 'reason': 'game-or-engine'}]}}
        found, counts = collect.readme_listings(source, text, COMMIT)
        self.assertEqual([row['key'] for row in found], ['gh:a/a'])
        self.assertEqual(found[0]['section'], 'RE > IDA Plugins')
        self.assertEqual(counts['excluded:game-or-engine'], 1)

    def test_pre_list_references_surveys_and_source_code(self):
        text = ('# PRE-list\n\n* A. Author, “A Survey of Protocol Reverse Engineering Approaches”, doi: 10.1109/SURVEY\n\n'
                '# Table of Contents\n\n# Source Code\n\n| Name | Link |\n|---|---|\n| Netzob [[3]](#3) | https://github.com/netzob/netzob |\n\n'
                '# References\n\n#### [3]\nG. Bossert. “Exploiting Semantic for the Automatic Reverse Engineering of Protocols”. In: X. 2014.\n')
        source = {'id': 'pre', 'repository': 'techge/PRE-list', 'path': 'README.md', 'scope': {}}
        found, _ = collect.pre_list_listings(source, text, COMMIT)
        keys = [row['key'] for row in found]
        self.assertIn('doi:10.1109/survey', keys)
        self.assertIn('gh:netzob/netzob', keys)
        self.assertIn(leads.title_key('Exploiting Semantic for the Automatic Reverse Engineering of Protocols'), keys)
        netzob = next(row for row in found if row['key'] == 'gh:netzob/netzob')
        self.assertEqual(netzob['label'], 'Netzob')


class FakeResponse:
    def __init__(self, body, headers=None):
        self.stream, self.headers = io.BytesIO(body), headers or {}

    def read(self, size=-1):
        return self.stream.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeOpener:
    def __init__(self, routes):
        self.routes, self.requests = routes, []

    def open(self, request, timeout=None):
        self.requests.append(request)
        value = self.routes(request) if callable(self.routes) else self.routes[request.full_url]
        if isinstance(value, Exception):
            raise value
        return FakeResponse(value) if isinstance(value, bytes) else value


class FakeClock:
    def __init__(self):
        self.now, self.slept = 0.0, []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds


def client(routes, token='t0ken', **kwargs):
    clock = FakeClock()
    opener = FakeOpener(routes)
    return collect.Client(token, opener=opener, clock=clock, sleep=clock.sleep, **kwargs), opener, clock


class ClientTest(unittest.TestCase):
    def test_routes_tokens_redirects_sizes_and_pacing(self):
        self.assertTrue(collect.allowed('https://api.github.com/graphql', 'POST'))
        self.assertTrue(collect.allowed('https://arxiv.org/html/2606.17398v2'))
        self.assertTrue(collect.allowed('https://huggingface.co/api/models?search=x'))
        for url in ('https://example.org/', 'http://arxiv.org/html/2606.17398', 'https://api.github.com/user',
                    'https://arxiv.org/abs/2606.17398', 'https://user:pw@huggingface.co/api/models'):
            with self.subTest(url):
                self.assertFalse(collect.allowed(url))
        fake, opener, clock = client({'https://huggingface.co/api/models?search=a': b'[]',
                                      'https://huggingface.co/api/models?search=b': b'[]',
                                      'https://api.github.com/graphql': b'{"data": {}}'})
        fake.fetch('https://huggingface.co/api/models?search=a')
        fake.fetch('https://huggingface.co/api/models?search=b')
        self.assertEqual(clock.slept, [0.5])
        self.assertNotIn('Authorization', opener.requests[0].headers)
        fake.graphql('query { x }')
        self.assertEqual(opener.requests[-1].headers['Authorization'], 'Bearer t0ken')
        with self.assertRaises(collect.SourceError) as caught:
            fake.fetch('https://example.org/')
        self.assertEqual(caught.exception.reason, 'redirect-blocked')
        moved = HTTPError('https://arxiv.org/html/1', 301, 'Moved', {'Location': 'https://evil.example/x'}, io.BytesIO())
        fake, _, _ = client(lambda request: moved)
        with self.assertRaises(collect.SourceError) as caught:
            fake.fetch('https://arxiv.org/html/2606.17398')
        self.assertEqual(caught.exception.reason, 'redirect-blocked')
        fake, _, _ = client(lambda request: b'x' * 100)
        with self.assertRaises(collect.SourceError) as caught:
            fake.fetch('https://huggingface.co/api/models?search=a', limit=10)
        self.assertEqual(caught.exception.reason, 'response-too-large')
        limited = HTTPError('https://huggingface.co/api/models', 429, 'Too Many', {}, io.BytesIO())
        fake, opener, _ = client(lambda request: limited)
        for _ in range(2):
            with self.assertRaises(collect.SourceError) as caught:
                fake.fetch('https://huggingface.co/api/models?search=a')
            self.assertEqual(caught.exception.reason, 'rate-limited')
        self.assertEqual(len(opener.requests), 1, 'a rate-limited host is not asked again')
        fake, _, _ = client(lambda request: b'{}', token='')
        with self.assertRaises(collect.SourceError) as caught:
            fake.graphql('query { x }')
        self.assertEqual(caught.exception.reason, 'token-unavailable')
        fake, _, _ = client(lambda request: b'[]', max_requests=1)
        fake.fetch('https://huggingface.co/api/models?search=a')
        with self.assertRaises(collect.SourceError) as caught:
            fake.fetch('https://huggingface.co/api/models?search=b')
        self.assertEqual(caught.exception.reason, 'request-budget')

    def test_github_files_must_match_their_git_blob(self):
        body = b'# List\n'
        good = collect.git_blob_sha(body)

        def graphql(text, oid):
            return json.dumps({'data': {'repository': {'isPrivate': False, 'defaultBranchRef': {'target': {
                'oid': COMMIT, 'file': {'oid': oid, 'object': {'byteSize': len(text), 'isBinary': False,
                                                               'isTruncated': False, 'text': text}}}}}}}).encode()
        fake, _, _ = client(lambda request: graphql(body.decode(), good))
        self.assertEqual(collect.github_file(fake, 'example/list', 'README.md'), (body, COMMIT, good))
        blob = json.dumps({'content': 'IyBPdGhlcgo='}).encode()  # "# Other\n": not the advertised blob

        def mismatch(request):
            return blob if '/git/blobs/' in request.full_url else graphql('# Changed\n', good)
        fake, _, _ = client(mismatch)
        with self.assertRaises(collect.SourceError) as caught:
            collect.github_file(fake, 'example/list', 'README.md')
        self.assertEqual(caught.exception.reason, 'git-blob-mismatch')


class OtherSourceTest(unittest.TestCase):
    def test_topic_search_screens_and_keeps_metadata(self):
        nodes = [repository_node('good/decompiler-tool', 1), repository_node('spam/thing', 2),
                 repository_node('other/web-app', 3, description='A todo list', repositoryTopics={'nodes': []}),
                 repository_node('only/topic', 4, description='An IDE', repositoryTopics={'nodes': [{'topic': {'name': 'debugger'}}]})]
        payload = json.dumps({'data': {'search': {'pageInfo': {'hasNextPage': False, 'endCursor': None}, 'nodes': nodes}}}).encode()
        fake, _, _ = client(lambda request: payload)
        source = {'id': 'github-topic-x', 'topic': 'debugger', 'limit': 50,
                  'scope': {'require': 'decompil|revers|debugg', 'rules': [{'pattern': '^gh:spam/', 'reason': 'unrelated'}]}}
        found, counts, extra = collect.topic_listings(fake, source)
        self.assertEqual([row['key'] for row in found], ['gh:good/decompiler-tool'])
        # The searched topic never satisfies the screen by itself.
        self.assertEqual(counts['excluded:unrelated'], 3)
        self.assertIn('gh:good/decompiler-tool', extra['metadata'])
        self.assertEqual(found[0]['evidence_url'], 'https://github.com/topics/debugger')

    def test_json_registry_applies_the_linking_policy(self):
        document = {'games': [{'url': 'https://github.com/decomp/game', 'title': 'Game', 'type': 'decompilation', 'platform': 'N64'},
                              {'url': 'https://github.com/recomp/game', 'title': 'Recomp', 'type': 'static-recomp'},
                              {'url': 'https://github.com/web/game', 'title': 'Web', 'type': 'decompilation', 'play_url': 'https://x'}]}
        raw = json.dumps(document).encode()
        with patch.object(collect, 'github_file', return_value=(raw, COMMIT, 'f' * 40)):
            found, counts, extra = collect.json_registry_listings(None, {
                'id': 'games', 'repository': 'SubmitGame/awesome-decomp-games', 'path': 'data/games.json', 'items': 'games',
                'url_field': 'url', 'name_field': 'title',
                'scope': {'kind': 'case-study', 'type_field': 'type', 'include_types': ['decompilation'], 'exclude_fields': ['play_url']}})
        self.assertEqual([row['key'] for row in found], ['gh:decomp/game'])
        self.assertEqual(counts['excluded:linking-policy'], 2)
        self.assertEqual((found[0]['section'], found[0]['kind']), ('decompilation · N64', 'case-study'))
        self.assertEqual(extra['revision'], COMMIT)

    def test_directory_registry_reads_one_link_per_verified_file(self):
        text = 'R2PM_BEGIN\nR2PM_GIT "https://github.com/radareorg/r2ghidra"\nR2PM_DESC "Ghidra decompiler for r2"\n'
        entries = [{'name': 'r2ghidra', 'type': 'blob', 'object': {'oid': collect.git_blob_sha(text.encode()), 'byteSize': len(text),
                                                                   'isTruncated': False, 'text': text}}]
        payload = json.dumps({'data': {'repository': {'isPrivate': False, 'defaultBranchRef': {'target': {
            'oid': COMMIT, 'file': {'object': {'entries': entries}}}}}}}).encode()
        fake, _, _ = client(lambda request: payload)
        source = {'id': 'radare2-pm', 'repository': 'radareorg/radare2-pm', 'path': 'db', 'scope': {'kind': 'tool'},
                  'url_pattern': r'^R2PM_GIT\s+"([^"\s]+)"', 'label_pattern': r'^R2PM_DESC\s+"([^"]{1,300})"'}
        found, _, extra = collect.directory_listings(fake, source)
        self.assertEqual((found[0]['key'], found[0]['label'], found[0]['section']), ('gh:radareorg/r2ghidra', 'r2ghidra', 'Ghidra decompiler for r2'))
        self.assertEqual(found[0]['evidence_url'], f'https://github.com/radareorg/radare2-pm/blob/{COMMIT}/db/r2ghidra')
        entries[0]['object']['oid'] = 'f' * 40
        payload = json.dumps({'data': {'repository': {'isPrivate': False, 'defaultBranchRef': {'target': {
            'oid': COMMIT, 'file': {'object': {'entries': entries}}}}}}}).encode()
        fake, _, _ = client(lambda request: payload)
        with self.assertRaises(collect.SourceError):
            collect.directory_listings(fake, source)

    def test_survey_bibliography_with_semantic_scholar_identifiers(self):
        page = ('<img src="2606.17398v2/figure.png"><ul>'
                '<li id="bib.bib1" class="ltx_bibitem">A. B. 2020. Neural decompilation of stripped binaries. In NDSS.</li>'
                '<li id="bib.bib2" class="ltx_bibitem">C. D. 2021. Attention is all you need, again. arXiv.</li>'
                '<li id="bib.bib3" class="ltx_bibitem">E. F. Ghidra. <a href="https://github.com/NationalSecurityAgency/ghidra">link</a></li>'
                '</ul>')
        references = {'data': [{'citedPaper': {'paperId': 'a' * 40, 'title': 'Neural Decompilation of Stripped Binaries',
                                               'externalIds': {'ArXiv': '2001.00001', 'DOI': '10.1145/X'}, 'year': 2020,
                                               'venue': 'NDSS'}}]}

        def route(request):
            return json.dumps(references).encode() if 'semanticscholar' in request.full_url else page.encode()
        fake, _, clock = client(route)
        source = {'id': 'survey-sok', 'paper_id': 'paper-sok', 'scope': {'paper_screen': 're-subject-v1'}}
        found, counts, extra = collect.survey_listings(fake, source, {'paper-sok': {'arxiv_id': '2606.17398', 'title': 'SoK'}})
        self.assertEqual([row['key'] for row in found], ['arxiv:2001.00001', 'gh:nationalsecurityagency/ghidra'])
        self.assertEqual(counts['excluded:not-re-subject'], 1)
        self.assertEqual(found[0]['paper']['doi'], '10.1145/x')
        self.assertEqual(found[0]['evidence_url'], 'https://arxiv.org/html/2606.17398v2#bib.bib1')
        self.assertEqual(extra['revision'], '2606.17398v2')

    def test_arxiv_feed_and_hugging_face_search(self):
        feed = ('<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">'
                '<entry><id>http://arxiv.org/abs/2611.02788v1</id><title>Rethinking Neural Decompilation</title>'
                '<published>2026-11-02T09:02:54Z</published><arxiv:doi>bad doi</arxiv:doi></entry>'
                '<entry><id>http://arxiv.org/abs/2611.00001v1</id><title>Scaling laws for chatbots</title>'
                '<published>2026-11-01T00:00:00Z</published></entry></feed>').encode()
        fake, _, _ = client(lambda request: feed)
        found, counts, _ = collect.arxiv_listings(fake, {'id': 'arxiv-x', 'query': 'abs:decompil*', 'limit': 10,
                                                         'scope': {'paper_screen': 're-subject-v1'}})
        self.assertEqual([row['key'] for row in found], ['arxiv:2611.02788'])
        self.assertEqual((found[0]['paper']['year'], found[0]['paper']['doi']), (2026, None))
        fake, _, _ = client(lambda request: b'<!DOCTYPE x [<!ENTITY a "b">]><feed/>')
        with self.assertRaises(collect.SourceError):
            collect.arxiv_listings(fake, {'id': 'arxiv-x', 'query': 'x', 'limit': 1, 'scope': {}})
        rows = [{'id': 'LLM4Binary/llm4decompile-6.7b', 'downloads': 10, 'likes': 2, 'lastModified': '2025-01-01T00:00:00.000Z'},
                {'id': 'someone/llm4decompile-6.7b-GGUF', 'downloads': 99, 'likes': 0}]
        fake, _, _ = client(lambda request: json.dumps(rows).encode())
        found, counts, _ = collect.huggingface_listings(fake, {'id': 'hf', 'repo_type': 'model', 'search': 'decompil', 'limit': 5,
                                                               'scope': {'exclude_text': 'gguf'}})
        self.assertEqual([row['key'] for row in found], ['huggingface:model/LLM4Binary/llm4decompile-6.7b'])
        self.assertEqual(found[0]['huggingface']['last_modified'], '2025-01-01T00:00:00Z')
        self.assertEqual(counts['excluded:unrelated'], 1)

    def test_slow_sources_run_once_per_period(self):
        source = {'id': 'survey-sok', 'every_hours': 24}
        start = dt.datetime(2026, 11, 5, 1, 7, tzinfo=dt.timezone.utc)
        runs = [collect.due(source, start + dt.timedelta(hours=slot), False) for slot in range(24)]
        self.assertEqual(sum(runs), 1)
        twelve = {'id': 'github-topic-x', 'every_hours': 12}
        self.assertEqual(sum(collect.due(twelve, start + dt.timedelta(hours=slot), False) for slot in range(24)), 2)
        two = {'id': 'x', 'every_hours': 2}
        self.assertEqual(sum(collect.due(two, start + dt.timedelta(hours=slot), False) for slot in range(24)), 12)
        self.assertTrue(collect.due(source, start, True))
        self.assertTrue(collect.due({'id': 'x'}, start, False))


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        import re
        self.text = (ROOT / '.github/workflows/discovery-leads.yml').read_text(encoding='utf-8')
        jobs = self.text.split('\njobs:\n', 1)[1]
        self.jobs = dict(zip(re.findall(r'^  ([a-z]+):$', jobs, re.MULTILINE), re.split(r'^  [a-z]+:$', jobs, flags=re.MULTILINE)[1:]))

    def test_read_only_collection_and_a_separate_writing_ingest(self):
        import re
        self.assertEqual(list(self.jobs), ['collect', 'ingest', 'report'])
        self.assertIn("cron: '7 * * * *'", self.text)
        self.assertIn('permissions:\n  contents: read\nconcurrency:\n  group: followed-source-lead-discovery\n  cancel-in-progress: false', self.text)
        writes = {name: re.findall(r'^      ([a-z-]+): write$', job, re.MULTILINE) for name, job in self.jobs.items()}
        self.assertEqual(writes, {'collect': [], 'ingest': ['contents', 'pull-requests', 'actions'], 'report': ['issues']})
        for name, job in self.jobs.items():
            self.assertLessEqual(int(re.search(r'timeout-minutes: ([0-9]+)', job)[1]), 45 if name == 'ingest' else 30, name)
            self.assertIn('persist-credentials: false', job)
        self.assertIn("needs.collect.outputs.collection_ready == 'true'", self.jobs['ingest'])
        self.assertIn('run: python3 scripts/collect_discovery_leads.py run', self.jobs['ingest'])
        self.assertIn('--tracker discovery-leads --result "collect=$COLLECT_RESULT" --result "ingest=$INGEST_RESULT"', self.jobs['report'])
        for line in self.text.splitlines():
            if line.strip().startswith('run:'):
                self.assertNotIn('${{', line)
        for line in self.text.splitlines():
            if 'uses:' in line:
                self.assertRegex(line, r'@[0-9a-f]{40} # v')


class SharedPageTest(unittest.TestCase):
    def test_a_page_listed_for_several_tools_becomes_one_lead_per_tool(self):
        page = 'https://hex-rays.example/contests/2018/index.shtml'
        key = leads.url_key(page)[0]
        rows = [listing('ida-list', page, key, label='HexRaysDeob'), listing('ida-list', page, key, label='Hyara'),
                listing('ida-list', page, key, label='nios2'), listing('other-list', page, key, label='Hyara'),
                listing('ida-list', 'https://example.org/single', 'url:example.org/single', label='Single')]
        collect.split_shared_pages(rows)
        self.assertEqual([row['key'] for row in rows], [key + '#hexraysdeob', key + '#hyara', key + '#nios2', key + '#hyara',
                                                         'url:example.org/single'])
        candidates, _ = collect.candidates_from(rows, {}, NOW)
        by_identity = {lead['identity']: lead for lead in candidates}
        self.assertEqual([row['source_id'] for row in by_identity[key + '#hyara']['listings']], ['ida-list', 'other-list'])
        for lead in candidates:
            self.assertEqual(leads.lead_problems(lead), [], lead['identity'])
        # The keys do not depend on listing order.
        reordered = [listing('ida-list', page, key, label=name) for name in ('nios2', 'Hyara', 'HexRaysDeob')]
        collect.split_shared_pages(reordered)
        self.assertEqual(sorted(row['key'] for row in reordered), sorted({key + '#hexraysdeob', key + '#hyara', key + '#nios2'}))

    def test_entries_of_a_project_page_do_not_merge_through_its_repository(self):
        page = 'https://owner.github.io/project/tools'
        key, _, flags = leads.url_key(page)
        self.assertEqual(flags['ghpages_alias'], 'gh:owner/project')
        rows = [{**listing('a-list', page, key, label=name), 'flags': dict(flags)} for name in ('First Tool', 'Second Tool')]
        collect.split_shared_pages(rows)
        candidates, _ = collect.candidates_from(rows, {'owner/project': repository_node('owner/project', 77)}, NOW)
        self.assertEqual(sorted(lead['identity'] for lead in candidates), sorted({key + '#firsttool', key + '#secondtool'}))

    def test_non_ascii_names_stay_distinct(self):
        page = 'https://tools.example/download'
        key = leads.url_key(page)[0]
        self.assertNotEqual(leads.entry_name('क'), leads.entry_name('कि'))
        self.assertEqual(leads.entry_name('Olly UST_2bg'), 'ollyust2bg')
        rows = [listing('cn-list', page, key, label='脱壳工具'), listing('cn-list', page, key, label='反调试插件')]
        collect.split_shared_pages(rows)
        self.assertEqual(len({row['key'] for row in rows}), 2)
        self.assertTrue(all(row['key'].startswith(key + '#') for row in rows))

    def test_an_entry_already_held_under_the_page_key_is_not_added_again(self):
        page = 'https://hex-rays.example/contests/2018/index.shtml'
        key = leads.url_key(page)[0]
        held, _ = collect.candidates_from([listing('ida-list', page, key, label='HexRaysDeob')], {}, NOW)
        existing = {'known': {}, 'records': 0, 'bytes': 0}
        for item in lead_keys_with_entry(held[0]):
            existing['known'][item] = 'already-lead'
        rows = [listing('ida-list', page, key, label='HexRaysDeob'), listing('ida-list', page, key, label='Hyara')]
        collect.split_shared_pages(rows)
        candidates, _ = collect.candidates_from(rows, {}, NOW)
        selected, _, skipped = leads.select_leads(candidates, existing, 10, ['ida-list'])
        self.assertEqual([lead['identity'] for lead in selected], [key + '#hyara'])
        self.assertEqual(skipped['already-lead'], 1)


class ProjectPageTest(unittest.TestCase):
    def test_a_project_page_of_a_held_repository_is_not_a_new_lead(self):
        page = 'https://owner.github.io/tool/'
        key, _, flags = leads.url_key(page)
        candidates, _ = collect.candidates_from([{**listing('a-list', page, key, label='Tool'), 'flags': dict(flags)}], {}, NOW)
        self.assertEqual(candidates[0]['identity'], key)
        self.assertIn('gh:owner/tool', leads.match_keys(candidates[0]))
        selected, _, skipped = leads.select_leads(candidates, {'known': {'gh:owner/tool': 'already-curated'}, 'records': 0, 'bytes': 0},
                                                  5, ['a-list'])
        self.assertEqual((selected, skipped['already-curated']), ([], 1))

    def test_an_entry_of_a_shared_project_page_is_not_its_repository(self):
        page = 'https://owner.github.io/project/tools'
        key, _, flags = leads.url_key(page)
        rows = [{**listing('a-list', page, key, label=name), 'flags': dict(flags)} for name in ('First Tool', 'Second Tool')]
        collect.split_shared_pages(rows)
        candidates, _ = collect.candidates_from(rows, {}, NOW)
        self.assertTrue(all('gh:owner/project' not in leads.match_keys(lead) for lead in candidates))


class SharedPageLimitsTest(unittest.TestCase):
    def test_long_entry_names_keep_a_digest(self):
        first, second = 'a' * 45 + 'one', 'a' * 45 + 'two'
        self.assertNotEqual(leads.shared_page_key('url:example.org/p', first), leads.shared_page_key('url:example.org/p', second))
        self.assertLessEqual(len(leads.shared_page_key('url:example.org/p', first).split('#', 1)[1]), 40)

    def test_a_queued_entry_taken_up_by_a_curated_page_is_counted_not_listed(self):
        curated = json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))
        record = next(row for row in curated if leads.url_key(row['url'])[0].startswith('url:'))
        page_key = leads.url_key(record['url'])[0]
        candidates, _ = collect.candidates_from([listing('example-list', record['url'], page_key, label=record['name'])], {}, NOW)
        lead = candidates[0]
        self.assertEqual(lead['identity'], page_key)
        with tempfile.TemporaryDirectory() as directory:
            root = lead_root(directory)
            held = leads.existing_keys(root, [])['known']
        self.assertTrue(leads.match_keys(lead) & held.keys())

    def test_a_case_ledger_page_is_known_as_the_entry_its_title_names(self):
        ledger = json.loads((ROOT / 'data/case-coverage.json').read_text(encoding='utf-8'))
        entry, url = next((row, url) for row in ledger['entries'] for url in row['reported_source_urls'] + row['primary_evidence_urls']
                          if (leads.url_key(url)[0] or '').startswith('url:') and ':' in row['title'])
        page_key = leads.url_key(url)[0]
        with tempfile.TemporaryDirectory() as directory:
            known = leads.existing_keys(lead_root(directory))['known']
        lead_name = entry['title'].split(':', 1)[0]
        self.assertEqual(known.get(leads.entry_key(leads.shared_page_key(page_key, leads.entry_name(lead_name)), '')), 'case-lead')
        self.assertNotIn(leads.entry_key(leads.shared_page_key(page_key, 'someothertool'), ''), known)

    def test_long_pages_stay_within_the_identity_limit_and_still_match(self):
        page_key = 'url:example.org/' + 'a' * 590
        split = leads.shared_page_key(page_key, 'toolname')
        self.assertLessEqual(len(split), 600)
        self.assertTrue(leads.IDENTITY.fullmatch(split))
        self.assertEqual(leads.entry_key(split, 'ignored'), leads.entry_key(page_key, 'Tool Name'))

    def test_a_curated_page_is_known_as_the_entry_with_its_own_name(self):
        curated = json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))
        record = next(row for row in curated if leads.url_key(row['url'])[0].startswith('url:'))
        page_key = leads.url_key(record['url'])[0]
        with tempfile.TemporaryDirectory() as directory:
            known = leads.existing_keys(lead_root(directory))['known']
        same = leads.entry_key(leads.shared_page_key(page_key, leads.entry_name(record['name'])), '')
        self.assertEqual(known.get(same), 'already-curated')
        other = leads.entry_key(leads.shared_page_key(page_key, 'someothertool'), '')
        self.assertNotIn(other, known)


def lead_keys_with_entry(lead):
    return leads.match_keys(lead)


class CandidateTest(unittest.TestCase):
    def test_one_candidate_per_resource_with_aliases_and_metadata(self):
        repositories = {'old/name': repository_node('new/name', 7), 'new/name': repository_node('new/name', 7),
                        'gone/repo': None, 'list/awesome-re': repository_node('list/awesome-re', 9)}
        rows = [listing('list-a', 'https://github.com/old/name', 'gh:old/name', label='Old'),
                listing('list-b', 'https://github.com/new/name', 'gh:new/name', label='New', kind='integration'),
                listing('list-a', 'https://github.com/gone/repo', 'gh:gone/repo'),
                listing('list-a', 'https://github.com/list/awesome-re', 'gh:list/awesome-re'),
                listing('survey', 'https://arxiv.org/abs/2001.00001', 'arxiv:2001.00001', kind='research',
                        paper={'title': 'Neural Decompilation of Stripped Binaries', 'arxiv_id': '2001.00001', 'doi': None}),
                listing('pre', 'https://example.org/x.pdf', leads.title_key('Neural decompilation of stripped binaries'), kind='research',
                        paper={'title': 'Neural decompilation of stripped binaries', 'doi': '10.1145/x', 'arxiv_id': None})]
        candidates, unavailable = collect.candidates_from(rows, repositories, NOW)
        self.assertEqual(unavailable, 1)
        by_identity = {lead['identity']: lead for lead in candidates}
        renamed = by_identity['github:7']
        self.assertEqual(renamed['aliases'], ['gh:new/name', 'gh:old/name'])
        self.assertEqual([row['source_id'] for row in renamed['listings']], ['list-a', 'list-b'])
        self.assertEqual((renamed['url'], renamed['kind_hint']), ('https://github.com/new/name', 'integration'))
        self.assertEqual(by_identity['github:9']['kind_hint'], 'collection')
        paper = by_identity['arxiv:2001.00001']
        self.assertEqual(paper['paper']['doi'], '10.1145/x')
        self.assertIn('doi:10.1145/x', paper['aliases'])
        self.assertEqual(paper['url'], 'https://arxiv.org/abs/2001.00001')
        for lead in candidates:
            self.assertEqual(leads.lead_problems(lead), [], lead['identity'])


class SelectionTest(unittest.TestCase):
    def test_skip_reasons_round_robin_and_limit(self):
        first = [github_lead(number, source='list-a') for number in range(1, 5)]
        second = [github_lead(number, source='list-b') for number in range(11, 13)]
        known = {'github:1': 'already-indexed', 'gh:owner2/tool2': 'already-curated', 'github:3': 'case-lead'}
        selected, eligible, skipped = leads.select_leads(first + second, {'known': known, 'records': 0, 'bytes': 0}, 2,
                                                         ['list-a', 'list-b'])
        # Sources take turns: list-a's first three are held, so list-b's two fill the limit and github:4 waits.
        self.assertEqual([lead['identity'] for lead in selected], ['github:11', 'github:12'])
        self.assertEqual(eligible, 3)
        self.assertEqual((skipped['already-indexed'], skipped['already-curated'], skipped['case-lead'], skipped['over-limit']),
                         (1, 1, 1, 1))

    def test_invalid_candidates_are_counted_and_never_published(self):
        lead = github_lead(1)
        lead['kind_hint'] = 'gadget'
        with patch('sys.stderr', new_callable=io.StringIO) as stderr:
            selected, eligible, skipped = leads.select_leads([lead, github_lead(2)], {'known': {}, 'records': 0, 'bytes': 0},
                                                             5, ['example-list'])
        self.assertEqual(([row['identity'] for row in selected], skipped['invalid']), (['github:2'], 1))
        self.assertIn(lead['id'], stderr.getvalue())

    def test_privacy_hits_are_skipped(self):
        import discoveries
        flagged = github_lead(5)
        with patch.object(discoveries, 'protected_identifier', side_effect=lambda value: value.get('id') == flagged['id']):
            selected, _, skipped = leads.select_leads([flagged, github_lead(6)], {'known': {}, 'records': 0, 'bytes': 0}, 5,
                                                      ['example-list'])
        self.assertEqual(([row['identity'] for row in selected], skipped['privacy']), (['github:6'], 1))

    def test_budget_stops_or_shrinks_a_batch(self):
        candidates = [github_lead(number) for number in range(1, 4)]
        self.assertEqual(leads.build_batch(candidates, source_results('example-list'), PROVENANCE,
                                           {'known': {}, 'records': leads.MAX_TOTAL_RECORDS, 'bytes': 0},
                                           collected_at=NOW, source_order=['example-list']), (None, 'budget-reached'))
        with patch.object(leads, 'MAX_BATCH_BYTES', len(leads.batch_bytes(make_batch(candidates[:2]))) + 10):
            batch, status = leads.build_batch(candidates, source_results('example-list'), PROVENANCE,
                                              {'known': {}, 'records': 0, 'bytes': 0}, collected_at=NOW,
                                              source_order=['example-list'])
        self.assertEqual((status, len(batch['leads']), batch['selection']['skipped_counts']['over-limit']), ('selected', 2, 1))


class BatchValidationTest(unittest.TestCase):
    def test_a_built_batch_is_valid(self):
        batch = make_batch([github_lead(1), web_lead('https://nostarch.com/practical-reversing')])
        self.assertEqual(leads.validate_batch(batch, batch['batch_id'], '2026-11'), [])
        self.assertEqual(batch['selection']['policy'], 'followed-source-leads-v1')

    def test_tampering_upgrades_and_bad_provenance_are_rejected(self):
        batch = make_batch([github_lead(1)])
        changes = {
            'upgraded': lambda value: value['leads'][0].update(review_status='source-reviewed'),
            'renamed': lambda value: value['leads'][0].update(name='Changed after selection'),
            'evidence': lambda value: value['leads'][0]['listings'][0].update(evidence_url='https://example.org/list'),
            'identity': lambda value: value['leads'][0].update(identity='github:2'),
            'provenance': lambda value: value['provenance'].update(workflow_path='.github/workflows/other.yml'),
            'run': lambda value: value['provenance'].update(run_id=1),
            'source': lambda value: value['leads'][0]['listings'][0].update(source_id='unrecorded'),
            'future': lambda value: value.update(collected_at='2099-01-01T00:00:00Z'),
        }
        for label, change in changes.items():
            altered = deepcopy(batch)
            change(altered)
            with self.subTest(label):
                self.assertNotEqual(leads.validate_batch(altered, batch['batch_id'], '2026-11'), [])
        self.assertNotEqual(leads.validate_batch(batch, batch['batch_id'], '2026-12'), [])

    def test_queue_files_identities_and_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = make_batch([github_lead(1)])
            again = make_batch([github_lead(1)], run_id=42100000002)
            for batch in (first, again):
                path = leads.batch_path(root, batch['batch_id'], batch['collected_at'])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(leads.batch_bytes(batch))
            batches, problems = leads.load_batches(root, now=dt.datetime(2026, 11, 6, tzinfo=dt.timezone.utc))
            self.assertEqual(len(batches), 2)
            self.assertIn('identity already belongs', ' '.join(problems))
            (root / leads.DIRECTORY / '2026-11' / 'notes.txt').write_text('x')
            self.assertIn('unexpected entries', ' '.join(leads.load_batches(root)[1]))


def lead_root(directory):
    """A copy of the repository data layers that the lead queue compares against."""
    root = Path(directory)
    for name in ('data/tool-resources.json', 'data/rea-resources.json', 'data/papers.json', 'data/source-index.json',
                 'data/source-scope.json', 'data/case-coverage.json'):
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, root / name)
    shutil.copytree(ROOT / 'data/source-supplements', root / 'data/source-supplements')
    (root / 'data/discoveries').mkdir(parents=True, exist_ok=True)
    return root


class LayersAndExportTest(unittest.TestCase):
    def test_existing_layers_and_prepare_and_site_export(self):
        curated = json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))
        github_record = next(record for record in curated if record['url'].startswith('https://github.com/'))
        indexed = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))['resources'][0]
        with tempfile.TemporaryDirectory() as directory:
            root = lead_root(directory)
            existing = leads.existing_keys(root)
            self.assertEqual(existing['known'][leads.url_key(github_record['url'])[0]], 'already-curated')
            self.assertEqual(existing['known']['github:' + indexed['id'][5:]], 'already-indexed')
            candidates = [github_lead(1), github_lead(int(indexed['id'][5:]), indexed['full_name'])]
            shutil.copy(ROOT / 'data/discovery-sources.json', root / 'data/discovery-sources.json')
            collection = {'candidates': candidates, 'sources': source_results('example-list'), 'collected_at': NOW,
                          'source_order': ['example-list'], 'unavailable': 0,
                          'registry_sha256': hashlib.sha256((root / 'data/discovery-sources.json').read_bytes()).hexdigest()}
            renamed = {**collection, 'held_keys': {'github:1': 'already-curated'}}
            self.assertEqual(collect.prepare(renamed, PROVENANCE, root=root)[1:], ('nothing-new', 0))
            stale = {**collection, 'registry_sha256': '0' * 64}
            self.assertEqual(collect.prepare(stale, PROVENANCE, root=root), (None, 'registry-changed', 0))
            path, status, count = collect.prepare(collection, PROVENANCE, root=root)
            self.assertEqual((status, count), ('selected', 1))
            self.assertEqual(path.relative_to(root).as_posix(), 'data/discoveries/leads/2026-11/leads-42100000001-1.json')
            self.assertEqual(collect.prepare(collection, PROVENANCE, root=root)[1], 'already-ingested')
            site = Path(directory) / 'site'
            catalog = {'meta': {'site_url': 'https://awesomerea.org', 'repository_url': 'https://github.com/reacher-z/Awesome-REA'}}
            queue = build_discovery_leads.write_lead_exports(site, catalog, root=root)
            export = json.loads((site / 'discoveries/leads.json').read_text(encoding='utf-8'))
            self.assertEqual([row['id'] for row in export['resources']], [candidates[0]['id']])
            self.assertEqual(export['review_status'], 'unreviewed')
            page = json.loads((site / 'discoveries/leads/leads-42100000001-1.json').read_text(encoding='utf-8'))
            self.assertEqual(page['resources'][0]['verification'], 'automated-source-lead')
            self.assertIn('Followed-source leads (unreviewed)', build_discovery_leads.llms_section(queue, 'https://awesomerea.org'))


class IngestScopeTest(unittest.TestCase):
    def test_only_a_lead_batch_is_committed_and_checks_target_the_leads_branch(self):
        from test_discovery_ingest import FakeAPI
        api = FakeAPI({('GET', 'git/commits/'): (200, {'tree': {'sha': 't' * 40}}),
                       ('POST', 'git/blobs'): (201, {'sha': 'b' * 40}), ('POST', 'git/trees'): (201, {'sha': 'n' * 40}),
                       ('POST', 'git/commits'): (201, {'sha': 'c' * 40}), ('PATCH', 'git/refs/heads/'): (200, {}),
                       ('POST', 'actions/workflows/'): (204, None)})
        path = ROOT / 'data/discoveries/leads/2026-11/leads-1-1.json'
        with patch.object(Path, 'read_bytes', return_value=b'{}\n'):
            self.assertEqual(collect.commit_batch(api, 'a' * 40, path, 'Add 1 lead'), 'c' * 40)
        self.assertIn(('PATCH', f'git/refs/heads/{leads.INGEST_BRANCH}', {'sha': 'c' * 40, 'force': True}), api.calls)
        for other in ('data/discoveries/run-1-1.json', 'data/tool-resources.json', 'data/discovery-sources.json'):
            with self.subTest(other), self.assertRaises(ValueError):
                collect.commit_batch(api, 'a' * 40, ROOT / other, 'x')
        collect.dispatch_checks(api, 'main', 42, 'f' * 40)
        self.assertEqual(api.calls[-2], ('POST', 'actions/workflows/validate.yml/dispatches', {'ref': leads.INGEST_BRANCH}))
        self.assertEqual(api.calls[-1][2]['inputs'], {'pr_number': '42', 'head_sha': 'f' * 40})


class MergeTest(unittest.TestCase):
    def test_the_batch_commit_is_rebase_merged_and_a_refusal_is_retried_while_current(self):
        from test_discovery_ingest import FakeAPI
        import ingest_discoveries as ingest
        answers = [ingest.ApiError(405, 'not mergeable yet'), (200, {'sha': 'm' * 40})]
        api = FakeAPI({('PUT', 'pulls/5/merge'): lambda endpoint, payload: answers.pop(0),
                       ('GET', 'branches/main'): (200, {'commit': {'sha': 'a' * 40}})})
        with patch.object(collect.time, 'sleep'):
            self.assertEqual(collect.merge_pull(api, 5, 'c' * 40, 'main', 'a' * 40), 'm' * 40)
        merges = [payload for method, endpoint, payload in api.calls if method == 'PUT']
        self.assertEqual(merges, [{'merge_method': 'rebase', 'sha': 'c' * 40}] * 2)
        moved = FakeAPI({('PUT', 'pulls/5/merge'): ingest.ApiError(405, 'Base branch was modified'),
                         ('GET', 'branches/main'): (200, {'commit': {'sha': 'b' * 40}})})
        with self.assertRaises(ingest.Retry):
            collect.merge_pull(moved, 5, 'c' * 40, 'main', 'a' * 40)


class LeadPullGitHub(FakeGitHub):
    def __init__(self, *args, user='github-actions[bot]', kind='Bot', ref=leads.INGEST_BRANCH, **kwargs):
        super().__init__(*args, **kwargs)
        self.pull_fields = {'user': {'login': user, 'type': kind}, 'ref': ref}

    def __call__(self, repository, endpoint, token, method='GET', payload=None, raw=False):
        result = super().__call__(repository, endpoint, token, method, payload, raw)
        if method == 'GET' and endpoint == f'pulls/{NUMBER}':
            return {**result, 'user': self.pull_fields['user'], 'head': {**result['head'], 'ref': self.pull_fields['ref']}}
        return result


class TrustedReviewTest(unittest.TestCase):
    def review(self, files, contents, **pull):
        github = LeadPullGitHub(files, contents, **pull)
        status, _ = run_review(github)
        return status, github.body()

    def batch_file(self, batch):
        return f"data/discoveries/leads/{batch['collected_at'][:7]}/{batch['batch_id']}.json"

    def test_a_workflow_batch_passes_and_others_need_a_maintainer(self):
        batch = make_batch([github_lead(910_000_001), web_lead('https://example.org/re-course')])
        name, text = self.batch_file(batch), leads.batch_bytes(batch).decode()
        status, body = self.review([{'filename': name, 'status': 'added'}], {name: text})
        self.assertEqual(status, 0, body)
        self.assertIn('Lead batch leads-42100000001-1: 2 followed-source leads', body)
        self.assertNotIn('not inspected', body)
        for pull in ({'user': 'someone', 'kind': 'User'}, {'ref': 'feature/hand-made'}):
            with self.subTest(pull):
                status, body = self.review([{'filename': name, 'status': 'added'}], {name: text}, **pull)
                self.assertEqual(status, 1)
                self.assertIn('added only by the followed-source discovery workflow', body)

    def test_edits_duplicates_and_upgrades_are_findings(self):
        batch = make_batch([github_lead(910_000_002)])
        name, text = self.batch_file(batch), leads.batch_bytes(batch).decode()
        status, body = self.review([{'filename': name, 'status': 'modified', 'patch': '@@ -1 +1 @@\n+x'}], {name: text})
        self.assertEqual(status, 1)
        self.assertIn('existing lead batches are immutable', body)
        indexed = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))['resources'][0]
        duplicate = make_batch([github_lead(int(indexed['id'][5:]), indexed['full_name'])])
        status, body = self.review([{'filename': name, 'status': 'added'}], {name: leads.batch_bytes(duplicate).decode()})
        self.assertEqual(status, 1)
        self.assertIn('already held by the repository', body)
        upgraded = deepcopy(batch)
        upgraded['leads'][0]['review_status'] = 'source-reviewed'
        status, body = self.review([{'filename': name, 'status': 'added'}], {name: leads.batch_bytes(upgraded).decode()})
        self.assertEqual(status, 1)

    def test_registry_changes_are_validated_with_base_rules(self):
        good = json.dumps(registry(), indent=2) + '\n'
        status, body = self.review([{'filename': review_pr.LEAD_REGISTRY, 'status': 'added', 'patch': '@@ -0,0 +1 @@\n+{}'}],
                                   {review_pr.LEAD_REGISTRY: good}, user='someone', kind='User', ref='feature/sources')
        self.assertEqual(status, 0, body)
        self.assertIn('Followed-source registry checked', body)
        bad = registry()
        bad['sources'][0]['type'] = 'ftp-list'
        status, body = self.review([{'filename': review_pr.LEAD_REGISTRY, 'status': 'modified', 'patch': '@@ -1 +1 @@\n+x'}],
                                   {review_pr.LEAD_REGISTRY: json.dumps(bad)}, user='someone', kind='User', ref='feature/sources')
        self.assertEqual(status, 1)
        self.assertIn('unknown source type', body)


if __name__ == '__main__':
    unittest.main()

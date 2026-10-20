"""Run the trusted PR reviewer end to end against an in-memory GitHub API; no network or token."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import review_pr


SHA, NEW_SHA, NUMBER, REPOSITORY = 'a' * 40, 'b' * 40, 7, 'example/catalog'


def fixture(*parts):
    # Credential-like and personal-path values are assembled at run time, so this file
    # never contains a value that the reviewer itself would report.
    return ''.join(parts)


TOKEN = fixture('gh', 'p_', 'Ab12' * 9)
KEY_HEADER = fixture('-----BEGIN ', 'ENCRYPTED PRIVATE KEY-----')
PERSONAL_PATHS = {
    'Linux home': fixture('/', 'home', '/alice/notes'),
    'final home segment': fixture('see /', 'home', '/alice'),
    'macOS home': fixture('/', 'Users', '/alice/Desktop'),
    'lowercase macOS home': fixture('/', 'users', '/alice/Desktop'),
    'Windows profile': fixture('C:', '\\Users\\alice\\Desktop\\capture.har'),
    'JSON-escaped Windows profile': fixture('C:', '\\\\Users\\\\alice\\\\Desktop'),
    'Windows forward slashes': fixture('C:/', 'Users', '/alice/'),
    'WSL mount': fixture('/mnt/c/', 'Users', '/alice/'),
    'Git Bash drive': fixture('/c/', 'Users', '/alice'),
    'home-relative tilde': fixture('~', '/captures/private.har'),
    'HOME variable': fixture('$HOME', '/captures/private.har'),
    'root home': fixture('/root', '/.config/gh/hosts.yml'),
}
# Raw JSON string text whose decoded value is a personal path or token.
ESCAPED_JSON = {
    'plain path': PERSONAL_PATHS['Linux home'],
    'slash-escaped path': fixture('\\/', 'home\\/alice\\/notes'),
    'unicode-escaped path': fixture('\\u002f', 'home\\u002falice\\u002fnotes'),
    'unicode-escaped token': fixture('\\u0067', 'hp_', 'Ab12' * 9),
}
ORDINARY_TEXT = [
    'patching login/root/premium checks', '修补登录/root/高级功能检查', '/absolute/path/to/app', 'site/', 'dist/ is generated',
    'https://www.usenix.org/system/files/sec24-presenter.pdf', 'https://github.com/users/octocat/projects',
    'https://github.com/example/skills/blob/main/docs/users/core.md', 'https://github.com/root-hunter/lenovo_bios',
    'https://example.edu/~alice/paper.pdf', 'GET /users/{id}', 'GET /users/:id/repos', 'GET /users/octocat',
    'const plain = text.replace(/~/g, "")', '~~old~~/new', 'export PATH before using $HOME', 'C:\\Program Files\\Tool',
    'run ./root/setup.sh', 'under /home or /Users', '-----BEGIN PUBLIC KEY-----', 'ghp_short', 'scripts/home/index.md',
    'GET /root/{id}', 'the `/root/` directory', '~/{config}', 'const route = /^\\/root\\/(.+)/',
]


def added(*lines):
    return '@@ -0,0 +1 @@\n' + '\n'.join('+' + line for line in lines)


def entry(filename, patch_text=None, status='modified', **extra):
    value = {'filename': filename, 'status': status, **extra}
    if patch_text is not None:
        value['patch'] = patch_text
    return value


def base(filename):
    return (ROOT / filename).read_text(encoding='utf-8')


def bot_review(identifier, commit=SHA, body=review_pr.MARKER, login='github-actions[bot]', kind='Bot'):
    return {'id': identifier, 'user': {'login': login, 'type': kind}, 'body': body, 'commit_id': commit}


class FakeGitHub:
    """Serve the REST endpoints used by the reviewer and record every request."""

    def __init__(self, files, contents=None, reviews=(), heads=(SHA, SHA), changed_files=None):
        self.files, self.contents, self.reviews, self.heads = files, contents or {}, list(reviews), list(heads)
        self.changed_files = len(files) if changed_files is None else changed_files
        self.requests, self.posted = [], []

    def __call__(self, repository, endpoint, token, method='GET', payload=None, raw=False):
        assert repository == REPOSITORY and token == 'test-token'
        self.requests.append((method, endpoint))
        path, _, query = endpoint.partition('?')
        params = dict(urllib.parse.parse_qsl(query))
        if method in ('POST', 'PUT'):
            self.posted.append((method, path, payload))
            return {}
        if path == f'pulls/{NUMBER}':
            return {'head': {'sha': self.heads.pop(0)}, 'changed_files': self.changed_files}
        if path in (f'pulls/{NUMBER}/files', f'pulls/{NUMBER}/reviews'):
            items = self.files if path.endswith('files') else self.reviews
            page, size = int(params['page']), int(params['per_page'])
            return items[(page - 1) * size:page * size]
        if path.startswith('contents/'):
            assert raw and params == {'ref': SHA}
            value = self.contents.get(urllib.parse.unquote(path[len('contents/'):]), OSError('Not Found'))
            if isinstance(value, Exception):
                raise value
            return value.decode('utf-8') if isinstance(value, bytes) else value
        raise AssertionError(f'Unexpected endpoint {endpoint}')

    def fetched(self):
        return [urllib.parse.unquote(endpoint.partition('?')[0][len('contents/'):])
                for _, endpoint in self.requests if endpoint.startswith('contents/')]

    def review_pages(self):
        return sum(endpoint.startswith(f'pulls/{NUMBER}/reviews?') for _, endpoint in self.requests)

    def body(self):
        return self.posted[-1][2]['body']


def run_review(github):
    with tempfile.TemporaryDirectory() as directory:
        event = Path(directory) / 'event.json'
        event.write_text(json.dumps({'pull_request': {'number': NUMBER}}))
        environment = {'GITHUB_TOKEN': 'test-token', 'GITHUB_REPOSITORY': REPOSITORY, 'GITHUB_EVENT_PATH': str(event)}
        output = io.StringIO()
        with patch.dict(os.environ, environment), patch.object(review_pr, 'api', github), \
                patch.object(review_pr.urllib.request, 'urlopen', side_effect=AssertionError('network access')), \
                contextlib.redirect_stdout(output):
            try:
                review_pr.main()
                status = 0
            except SystemExit as exit_status:
                status = exit_status.code
    return status, output.getvalue()


class ReviewerDataSelectionTest(unittest.TestCase):
    def test_changed_json_is_fetched_at_head_and_dependencies_come_from_base(self):
        github = FakeGitHub([entry(review_pr.SOURCE_SCOPE, added('x'))],
                            {review_pr.SOURCE_SCOPE: base(review_pr.SOURCE_SCOPE)})
        self.assertEqual(run_review(github)[0], 0)
        # The source index and locale files are validated, but only the changed file is fetched.
        self.assertEqual(github.fetched(), [review_pr.SOURCE_SCOPE])
        self.assertIn('repository localizations checked', github.body())
        self.assertIn('**No issues found by these automatic checks.**', github.body())
        self.assertEqual(github.posted, [('POST', f'pulls/{NUMBER}/reviews',
                                          {'commit_id': SHA, 'event': 'COMMENT', 'body': github.body()})])

    def test_current_data_raises_no_finding(self):
        names = sorted(review_pr.REVIEW_FILES)
        github = FakeGitHub([entry(name, added(*base(name).splitlines())) for name in names],
                            {name: base(name) for name in names})
        status, output = run_review(github)
        self.assertEqual((status, sorted(github.fetched())), (0, names))
        self.assertNotIn('Findings:', github.body())
        self.assertIn('0 finding(s), 0 file(s) not inspected', output)

    def test_removed_or_renamed_data_requires_maintainer_review(self):
        github = FakeGitHub([entry('data/benchmarks.json', '@@ -1 +0,0 @@\n-[]', status='removed'),
                             entry('data/papers-archive.json', added('x'), status='renamed',
                                   previous_filename='data/papers.json')])
        self.assertEqual(run_review(github)[0], 1)
        body = github.body()
        for filename in ('data/benchmarks.json', 'data/papers.json'):
            self.assertIn(review_pr.safe_text(f'{filename}: removing or renaming catalog'), body)
        self.assertEqual(github.fetched(), [])

    def test_files_with_patches_outside_the_allowlist_are_never_fetched(self):
        github = FakeGitHub([entry('docs/automation.md', added('Updated text.')),
                             entry('scripts/tool.py', added('print("ok")')),
                             entry('site/app.js', added('export const ready = true;')),
                             entry('data/locales/repositories-9.json', added('{}'), status='added')])
        self.assertEqual(run_review(github)[0], 1)
        self.assertEqual(github.fetched(), [])
        self.assertIn('locale file is not in the trusted review allowlist', github.body())
        self.assertIn('Code, automation, or site changes require a maintainer', github.body())


class ReviewerPrivacyTest(unittest.TestCase):
    def test_added_values_are_reported_without_repeating_them(self):
        for name, value in {**PERSONAL_PATHS, 'token': TOKEN, 'private key': KEY_HEADER}.items():
            with self.subTest(name):
                github = FakeGitHub([entry('docs/notes.md', added('Context.', f'Saved at {value} today.'))])
                self.assertEqual(run_review(github)[0], 1)
                body = github.body()
                self.assertIn('added text contains a credential-like value or personal path', body)
                for hidden in (value, 'alice', TOKEN[4:], 'ENCRYPTED'):
                    self.assertNotIn(hidden, body)

    def test_decoded_json_strings_in_changed_data_are_reported(self):
        papers = json.loads(base('data/papers.json'))
        papers[0]['metadata_notes'] = 'PLACEHOLDER'
        template = json.dumps(papers, ensure_ascii=False, indent=2)
        for name, raw in ESCAPED_JSON.items():
            with self.subTest(name):
                text = template.replace('"PLACEHOLDER"', f'"Notes kept in {raw}"')
                # Without a patch, only the fetched full content can reveal the value.
                github = FakeGitHub([entry('data/papers.json')], {'data/papers.json': text})
                self.assertEqual(run_review(github)[0], 1)
                body = github.body()
                self.assertIn(review_pr.safe_text(f'record {papers[0]["id"]}, field metadata_notes contains'), body)
                for hidden in (raw, json.loads(f'"{raw}"'), 'alice', 'Ab12Ab12'):
                    self.assertNotIn(hidden, body)

    def test_json_locations_use_safe_record_ids_and_fields(self):
        value = PERSONAL_PATHS['Linux home']
        locales = json.dumps({'scan-1': {'description_en': 'Plain.'}, 'scan-2': {'description_zh': value}})
        self.assertEqual(review_pr.json_privacy_findings('data/locales/repositories-1.json', locales),
                         ['data/locales/repositories-1.json: a decoded JSON string in record scan-2, field description_zh '
                          'contains a credential-like value or personal path; inspect locally. The value is omitted here.'])
        unsafe = json.dumps([{'id': value, 'notes': value}, {'id': 'ok', value: 'key'}])
        findings = review_pr.json_privacy_findings('data/papers.json', unsafe)
        self.assertEqual([finding.split(' contains')[0] for finding in findings],
                         ['data/papers.json: a decoded JSON string in field id', 'data/papers.json: a decoded JSON string in field notes',
                          'data/papers.json: a decoded JSON string in record ok'])
        self.assertTrue(all(value not in finding and 'alice' not in finding for finding in findings))
        self.assertIn('full JSON content contains', review_pr.json_privacy_findings('data/papers.json', '[' + json.dumps(value))[0])
        self.assertEqual(review_pr.json_privacy_findings('data/papers.json', json.dumps([{'id': 'ok', 'notes': ORDINARY_TEXT}])), [])

    def test_personal_path_forms_are_detected_and_redacted(self):
        for name, value in PERSONAL_PATHS.items():
            with self.subTest(name):
                self.assertTrue(review_pr.private_text(value))
                redacted = review_pr.safe_text(value)
                self.assertIn('\\[redacted local path\\]', redacted)
                self.assertNotIn('alice', redacted)

    def test_ordinary_urls_paths_and_code_are_not_flagged(self):
        for text in ORDINARY_TEXT:
            with self.subTest(text):
                self.assertFalse(review_pr.private_text(text))
                self.assertNotIn('redacted', review_pr.safe_text(text))

    def test_safe_text_escapes_markup_strips_controls_and_breaks_mentions(self):
        text = review_pr.safe_text('Ping @maintainer <img src=x> *bold* [link](u) `code`\u202e\u2066 #1 ' + TOKEN)
        self.assertNotIn('<img', text)
        self.assertIn('&lt;img', text)
        self.assertIn('@\u200bmaintainer', text)
        self.assertIn('\\*bold\\*', text)
        self.assertIn('\\[link\\]\\(u\\)', text)
        self.assertIn('\\`code\\`', text)
        self.assertNotIn('\u202e', text)
        self.assertNotIn('\u2066', text)
        self.assertNotIn(TOKEN, text)
        self.assertEqual(review_pr.safe_text('Notes in ' + ESCAPED_JSON['slash-escaped path']).count('redacted'), 1)
        for hidden in (TOKEN[:3] + '\x01' + TOKEN[3:], TOKEN[:3] + '\u202e' + TOKEN[3:], KEY_HEADER.replace(' ', '\n', 1),
                       PERSONAL_PATHS['Linux home'].replace('home', 'ho\x00me')):
            with self.subTest(repr(hidden)):
                self.assertIn('redacted', review_pr.safe_text(hidden))
                self.assertNotIn('Ab12', review_pr.safe_text(hidden))
                self.assertNotIn('alice', review_pr.safe_text(hidden))


class ReviewerOmittedPatchTest(unittest.TestCase):
    def test_patch_less_text_files_are_fetched_and_checked(self):
        github = FakeGitHub([entry('docs/large.md'), entry('docs/data.json'), entry('docs/clean.md', status='added')],
                            {'docs/large.md': 'Intro\n' + PERSONAL_PATHS['Windows profile'],
                             'docs/data.json': '{"k": "' + ESCAPED_JSON['unicode-escaped token'] + '"}',
                             'docs/clean.md': 'Plain text.'})
        self.assertEqual(run_review(github)[0], 1)
        self.assertEqual(github.fetched(), ['docs/large.md', 'docs/data.json', 'docs/clean.md'])
        body = github.body()
        self.assertEqual(body.count('GitHub omitted this diff, and the file text at this commit contains'), 2)
        self.assertNotIn('Not inspected', body)
        self.assertNotIn('alice', body)

    def test_binary_oversize_and_unavailable_files_are_not_counted_clean(self):
        github = FakeGitHub([entry('assets/logo.png', status='added'), entry('docs/huge.json'),
                             entry('docs/missing.md'), entry('docs/nul.txt'), entry('docs/moved.md', status='renamed')],
                            {'assets/logo.png': b'\x89PNG\r\n\x1a\n\x00', 'docs/huge.json': ValueError('too large'),
                             'docs/nul.txt': 'text\x00more', 'docs/moved.md': 'Plain text.'})
        status, output = run_review(github)
        self.assertEqual(status, 0)
        body = github.body()
        self.assertNotIn('**No issues found by these automatic checks.**', body)
        self.assertIn('**No issues found by these automatic checks, but 4 changed file(s) were not inspected.**', body)
        listed = body.split('Not inspected automatically:')[1]
        for filename in ('assets/logo.png', 'docs/huge.json', 'docs/missing.md', 'docs/nul.txt'):
            self.assertIn(review_pr.safe_text(filename), listed)
        self.assertNotIn('moved', listed)
        self.assertIn('0 finding(s), 4 file(s) not inspected', output)

    def test_patch_less_fetches_are_bounded(self):
        names = [f'docs/page-{index:02}.md' for index in range(review_pr.MAX_OMITTED_FILES + 5)]
        github = FakeGitHub([entry(name) for name in names], {name: 'Plain text.' for name in names})
        self.assertEqual(run_review(github)[0], 0)
        self.assertEqual(github.fetched(), names[:review_pr.MAX_OMITTED_FILES])
        self.assertIn('but 5 changed file(s) were not inspected', github.body())

    def test_omitted_text_uses_the_size_bounded_raw_fetch(self):
        class Response:
            def __init__(self, data):
                self.data, self.sizes = data, []

            def __enter__(self):
                return self

            def __exit__(self, *details):
                return False

            def read(self, size):
                self.sizes.append(size)
                return self.data[:size]

        for data, error in ((b'a' * (review_pr.MAX_FILE_BYTES + 10), ValueError), (b'\x89PNG\r\n', UnicodeError), (b'a\x00b', UnicodeError)):
            response = Response(data)
            with self.subTest(error=error.__name__, size=len(data)), \
                    patch.object(review_pr.urllib.request, 'urlopen', return_value=response) as urlopen:
                with self.assertRaises(error):
                    review_pr.omitted_text_at(REPOSITORY, 'docs/large file.md', SHA, 'test-token')
                request = urlopen.call_args[0][0]
                self.assertEqual(request.full_url, f'https://api.github.com/repos/{REPOSITORY}/contents/docs/large%20file.md?ref={SHA}')
                self.assertEqual((request.get_method(), request.get_header('Accept')), ('GET', 'application/vnd.github.raw+json'))
                self.assertEqual(response.sizes, [review_pr.MAX_FILE_BYTES + 1])

    def test_omitted_text_helper_refuses_allowlisted_private_and_unsafe_paths(self):
        with patch.object(review_pr, 'api') as api:
            for filename in ('data/papers.json', 'deploy/site.pem', '../outside.md', '/abs.md', 'docs//x.md', 'docs/./x.md'):
                with self.subTest(filename), self.assertRaises(ValueError):
                    review_pr.omitted_text_at(REPOSITORY, filename, SHA, 'test-token')
            api.assert_not_called()


class PrivateFileRulesTest(unittest.TestCase):
    FLAGGED = ['deploy/site.pem', 'deploy/site.key', 'config.local.json', '.cloudflare/pages.json', 'id_rsa',
               'keys/id_ed25519', 'docs/captures/session.har', 'assets/trace.pcapng', 'captures/dump.pcap', '.env',
               '.env.production', 'web/.env.local', 'secrets.json', 'credentials-prod.json', '.wrangler/state.json',
               'dist/index.html', 'labs/a/output/run.log', 'node_modules/x/index.js', '.venv/bin/python',
               'site/fonts/pro.woff2', 'scripts/__pycache__/x.pyc', '.DS_Store', 'DEPLOY/SITE.PEM']
    PUBLIC = ['.env.example', 'web/.env.example', 'keys/id_rsa.pub', 'site/app.js', 'docs/website.md',
              'data/papers.json', 'site/translations.zh-CN.json', 'docs/key-findings.md', 'assets/logo.png']

    def test_private_and_generated_paths_are_flagged_by_name(self):
        for path in self.FLAGGED:
            with self.subTest(path):
                self.assertIsNotNone(review_pr.path_rule(path))
        for path in self.PUBLIC:
            with self.subTest(path):
                self.assertIsNone(review_pr.path_rule(path))

    def test_every_gitignore_pattern_has_a_reviewer_rule(self):
        patterns = [line.strip() for line in (ROOT / '.gitignore').read_text().splitlines()
                    if line.strip() and not line.startswith('#')]
        self.assertTrue(patterns)
        for pattern in patterns:
            sample = pattern.lstrip('!').replace('**', 'a').replace('*', 'sample').replace('[cod]', 'c')
            samples = [sample + 'file.txt' if sample.endswith('/') else sample]
            if '/' not in sample.rstrip('/'):
                samples.append('nested/' + samples[0])
            for path in samples:
                with self.subTest(pattern=pattern, path=path):
                    if pattern.startswith('!'):
                        self.assertIsNone(review_pr.path_rule(path))
                    else:
                        self.assertIsNotNone(review_pr.path_rule(path))

    def test_removing_a_private_file_is_not_a_finding(self):
        github = FakeGitHub([entry('deploy/site.pem', '@@ -1 +0,0 @@\n-old', status='removed'),
                             entry('dist/index.html', status='removed')])
        self.assertEqual(run_review(github)[0], 0)
        self.assertEqual(github.fetched(), [])
        self.assertIn('**No issues found by these automatic checks.**', github.body())

    def test_pr_files_are_flagged_without_fetching_them(self):
        files = [entry('deploy/site.pem', added(fixture('-----BEGIN ', 'PRIVATE KEY-----'), 'MIIB')),
                 entry('deploy/site.key', added(KEY_HEADER, 'MIIB')), entry('config.local.json', added('{}')),
                 entry('.cloudflare/pages.json', added('{}')), entry('id_rsa', status='added'),
                 entry('docs/captures/session.har', status='added'), entry('assets/trace.pcapng', status='added'),
                 entry('.env.example', added('API_URL='))]
        github = FakeGitHub(files)
        self.assertEqual(run_review(github)[0], 1)
        self.assertEqual(github.fetched(), [])
        findings = github.body().split('Findings:')[1]
        for item in files[:-1]:
            self.assertIn(review_pr.safe_text(item['filename'] + ': '), findings)
        self.assertNotIn('env\\.example', findings)
        self.assertNotIn('ENCRYPTED', findings)
        self.assertNotIn('Not inspected', github.body())

    def test_tracked_files_raise_no_privacy_finding(self):
        try:
            listed = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            self.skipTest('git file list unavailable')
        paths = [path for path in listed.decode('utf-8').split('\0') if path]
        self.assertEqual([path for path in paths if review_pr.path_rule(path)], [])
        flagged = []
        for path in paths:
            try:
                text = (ROOT / path).read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue
            if review_pr.private_text(text):
                flagged.append(path)
        self.assertEqual(flagged, [])


class ReviewerPostingTest(unittest.TestCase):
    def test_more_than_30_findings_are_truncated(self):
        github = FakeGitHub([entry(f'docs/page-{index:02}.md', added(TOKEN)) for index in range(35)])
        self.assertEqual(run_review(github)[0], 1)
        findings = github.body().split('Findings:')[1].split('\n\n')[0].strip().splitlines()
        self.assertEqual(len(findings), 31)
        self.assertEqual(findings[-1], '- 5 additional findings; run the local validator for the complete list.')

    def test_changed_head_before_posting_posts_nothing(self):
        github = FakeGitHub([entry('docs/page.md', added(TOKEN))], heads=(SHA, NEW_SHA))
        status, output = run_review(github)
        self.assertEqual((status, github.posted), (0, []))
        self.assertIn('PR head changed', output)

    def test_existing_bot_review_for_the_commit_is_updated(self):
        github = FakeGitHub([entry('docs/page.md', added('Plain text.'))], reviews=[bot_review(5, commit=NEW_SHA), bot_review(9)])
        self.assertEqual(run_review(github)[0], 0)
        self.assertEqual([(method, path) for method, path, _ in github.posted], [('PUT', f'pulls/{NUMBER}/reviews/9')])
        self.assertEqual(set(github.posted[0][2]), {'body'})

    def test_null_users_are_skipped_and_later_review_pages_are_read(self):
        reviews = [{'id': 1, 'user': None, 'body': None, 'commit_id': SHA}]
        reviews += [bot_review(index, login='someone', kind='User') for index in range(2, 101)] + [bot_review(150)]
        github = FakeGitHub([entry('docs/page.md', added('Plain text.'))], reviews=reviews)
        self.assertEqual(run_review(github)[0], 0)
        self.assertEqual([(method, path) for method, path, _ in github.posted], [('PUT', f'pulls/{NUMBER}/reviews/150')])
        self.assertEqual(github.review_pages(), 2)

    def test_review_lookup_is_bounded(self):
        reviews = [{'id': index, 'user': None, 'body': 'Older review', 'commit_id': SHA} for index in range(1200)]
        github = FakeGitHub([entry('docs/page.md', added('Plain text.'))], reviews=reviews + [bot_review(5000)])
        self.assertEqual(run_review(github)[0], 0)
        self.assertEqual(github.review_pages(), review_pr.MAX_REVIEW_PAGES)
        self.assertEqual([method for method, _, _ in github.posted], ['POST'])

    def test_matching_requires_bot_login_type_marker_and_commit(self):
        for review in (bot_review(1, login='someone'), bot_review(2, kind='User'),
                       bot_review(3, body='No marker'), bot_review(4, commit=NEW_SHA)):
            with self.subTest(review['id']):
                github = FakeGitHub([entry('docs/page.md', added('Plain text.'))], reviews=[review])
                self.assertEqual(run_review(github)[0], 0)
                self.assertEqual([method for method, _, _ in github.posted], ['POST'])


if __name__ == '__main__':
    unittest.main()

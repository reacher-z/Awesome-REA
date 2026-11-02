"""Auth isolation: tokens only reach the configured API origin and never cross redirects."""
import sys
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from classify_evidence_classes import HttpClient, _AuthStrippingRedirect  # noqa: E402

TOKEN = 'test-token-not-real'


class HttpClientAuthTests(unittest.TestCase):
    def setUp(self):
        self.client = HttpClient(TOKEN, 'awesome-rea-test')

    def test_token_is_sent_only_to_the_api_origin(self):
        self.assertEqual(self.client.headers_for('https://api.github.com/repos/acme/foo')['Authorization'],
                         'Bearer ' + TOKEN)
        for url in ('https://gitlab.com/api/v4/projects/1', 'https://github.com/acme/foo',
                    'https://example.com/page', 'http://api.github.com/repos/acme/foo'):
            self.assertNotIn('Authorization', self.client.headers_for(url), url)

    def test_page_requests_never_carry_a_token(self):
        self.assertNotIn('Authorization', self.client.headers_for('https://api.github.com/repos/acme/foo', page=True))

    def test_cross_origin_redirect_drops_the_token(self):
        request = urllib.request.Request('https://api.github.com/repos/acme/foo',
                                         headers={'Authorization': 'Bearer ' + TOKEN})
        redirected = _AuthStrippingRedirect().redirect_request(
            request, None, 302, 'Found', {}, 'https://evil.example/steal')
        self.assertIsNotNone(redirected)
        self.assertNotIn('Authorization', redirected.headers)
        self.assertNotIn('Authorization', redirected.unredirected_hdrs)

    def test_same_origin_redirect_keeps_the_token(self):
        request = urllib.request.Request('https://api.github.com/repos/acme/foo',
                                         headers={'Authorization': 'Bearer ' + TOKEN})
        redirected = _AuthStrippingRedirect().redirect_request(
            request, None, 302, 'Found', {}, 'https://api.github.com/repos/acme/bar')
        self.assertIsNotNone(redirected)
        self.assertEqual(redirected.headers.get('Authorization'), 'Bearer ' + TOKEN)


if __name__ == '__main__':
    unittest.main()

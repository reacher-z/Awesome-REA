"""The evidence collector sends its token only to the GitHub API origin."""
import io
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collect_quality_evidence as evidence  # noqa: E402


class _Response(io.BytesIO):
    def __init__(self, body: bytes):
        super().__init__(body)
        self.status = 200
        self.headers = {"Content-Type": "application/json"}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _Opener:
    def __init__(self):
        self.requests = []

    def open(self, request, timeout=30):
        self.requests.append(request)
        return _Response(b'{"ok": true}')


class AuthIsolationTests(unittest.TestCase):
    def client(self, token="placeholder-token"):
        client = evidence.HttpClient(token, offline=False)
        client.cache_dir = Path(tempfile.mkdtemp(prefix="quality-http-"))
        client.opener = _Opener()
        return client

    def test_token_is_sent_only_to_api_github_com(self):
        client = self.client()
        client.get("https://api.github.com/repos/acme/demo", accept="application/json")
        client.get("https://example.org/public/page", accept="text/html", page=True)
        api_request, page_request = client.opener.requests
        self.assertEqual(api_request.get_header("Authorization"), "Bearer placeholder-token")
        self.assertIsNone(page_request.get_header("Authorization"))

    def test_cross_origin_redirect_drops_the_authorization_header(self):
        handler = evidence._AuthStrippingRedirect()
        request = urllib.request.Request(
            "https://api.github.com/repos/acme/demo",
            headers={"Authorization": "Bearer placeholder-token"},
        )
        redirected = handler.redirect_request(
            request, None, 302, "Found", {},
            "https://downloads.example.org/artifact.tar.gz",
        )
        self.assertIsNotNone(redirected)
        self.assertIsNone(redirected.get_header("Authorization"))

    def test_same_origin_redirect_keeps_the_authorization_header(self):
        handler = evidence._AuthStrippingRedirect()
        request = urllib.request.Request(
            "https://api.github.com/repos/acme/demo",
            headers={"Authorization": "Bearer placeholder-token"},
        )
        redirected = handler.redirect_request(
            request, None, 302, "Found", {},
            "https://api.github.com/repositories/1",
        )
        self.assertEqual(redirected.get_header("Authorization"), "Bearer placeholder-token")


if __name__ == "__main__":
    unittest.main()

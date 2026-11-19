import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fetch_previews  # noqa: E402

URL = "https://raw.githubusercontent.com/example/repo/0123456789abcdef/docs/shot.png"
IMAGE = b"served image"


def copies(**overrides):
    key = fetch_previews.cache_key(URL)
    files = {"previews/a.png": {"sha256": hashlib.sha256(IMAGE).hexdigest(), "bytes": len(IMAGE)}}
    return fetch_previews.SiteCopies({"a": {"key": key, "file": "a.png"}}, {**files, **overrides})


class FetchPreviewsTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        patcher = mock.patch.object(fetch_previews, "CACHE_DIR", Path(self.directory.name))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(mock.patch.object(fetch_previews.time, "sleep").start().stop)

    def test_a_served_copy_is_stored_under_the_url_key_and_used_before_the_host(self):
        with mock.patch.object(fetch_previews, "read_site", return_value=IMAGE), \
                mock.patch.object(fetch_previews, "download") as download:
            self.assertEqual(fetch_previews.fetch(URL, "a", copies()), "from-site")
            self.assertEqual(fetch_previews.cached_path(URL).read_bytes(), IMAGE)
            self.assertEqual(fetch_previews.fetch(URL, "a", copies()), "cached")
            download.assert_not_called()

    def test_a_served_copy_of_another_url_or_with_other_bytes_is_refused(self):
        with mock.patch.object(fetch_previews, "read_site", return_value=b"tampered"):
            self.assertFalse(copies().fetch("a", URL))
        with mock.patch.object(fetch_previews, "read_site", return_value=IMAGE):
            self.assertFalse(copies().fetch("a", URL + "x"))
            self.assertFalse(copies().fetch("b", URL))
        self.assertIsNone(fetch_previews.cached_path(URL))

    def test_site_only_never_reaches_the_host(self):
        with mock.patch.object(fetch_previews, "download") as download:
            self.assertEqual(fetch_previews.fetch(URL, "a", None, True), "not-on-site")
            download.assert_not_called()

    def test_an_unreachable_host_is_retried_before_the_image_is_dropped(self):
        with mock.patch.object(fetch_previews, "download", side_effect=["unreachable", "unreachable", "downloaded"]) as download:
            self.assertEqual(fetch_previews.fetch(URL), "downloaded")
            self.assertEqual(download.call_count, 3)
        with mock.patch.object(fetch_previews, "download", return_value="unreachable") as download:
            self.assertEqual(fetch_previews.fetch(URL), "unreachable")
            self.assertEqual(download.call_count, fetch_previews.ATTEMPTS)
        with mock.patch.object(fetch_previews, "download", return_value="empty") as download:
            self.assertEqual(fetch_previews.fetch(URL), "empty")
            self.assertEqual(download.call_count, 1)


if __name__ == "__main__":
    unittest.main()

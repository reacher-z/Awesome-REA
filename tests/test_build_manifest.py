"""Regression checks for CDN-only transformations in deployment verification."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_manifest import html_digest, normalized_html_bytes


def protected(address, key=108):
    encoded = bytes([key] + [byte ^ key for byte in address.encode()]).hex()
    return '<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="' + encoded + '">[email&#160;protected]</a>'


class CDNNormalizationTests(unittest.TestCase):
    decoder = '<script data-cfasync="false" src="/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js"></script>'

    def test_public_email_and_decoder_preserve_expected_text(self):
        for key in (0, 108, 255):
            self.assertEqual(normalized_html_bytes(('<p>Contact: ' + protected('contact@example.org', key) + '</p>' + self.decoder + '\n').encode()), b'<p>Contact: contact@example.org</p>\n')

    def test_email_content_stays_hash_sensitive(self):
        self.assertNotEqual(html_digest(b'<p>contact@example.org</p>'), html_digest(('<p>' + protected('different@example.org') + '</p>').encode()))

    def test_email_looking_literals_preserve_script_and_raw_text(self):
        anchor = protected('contact@example.org')
        contexts = {
            'script': '<script>const source = ' + repr(anchor) + ';</script>',
            'style': '<style>p::after{content:' + repr(anchor) + '}</style>',
            'comment': '<!-- ' + anchor + ' -->',
            'textarea': '<textarea>' + anchor + '</textarea>',
            'title': '<title>' + anchor + '</title>',
            'xmp': '<xmp>' + anchor + '</xmp>',
            'iframe': '<iframe>' + anchor + '</iframe>',
            'noembed': '<noembed>' + anchor + '</noembed>',
            'noframes': '<noframes>' + anchor + '</noframes>',
            'noscript': '<noscript>' + anchor + '</noscript>',
        }
        for context, document in contexts.items():
            with self.subTest(context=context):
                self.assertEqual(normalized_html_bytes(document.encode()), document.encode())

    def test_visible_email_does_not_normalize_identical_script_literal(self):
        anchor = protected('contact@example.org')
        script = '<script>const source = ' + repr(anchor) + ';</script>'
        document = '<div><p>' + anchor + '</p></div>' + script + self.decoder
        expected = '<div><p>contact@example.org</p></div>' + script
        self.assertEqual(normalized_html_bytes(document.encode()), expected.encode())
        changed_script = script.replace(anchor, 'contact@example.org')
        self.assertNotEqual(html_digest(script.encode()), html_digest(changed_script.encode()))

    def test_nonvoid_self_closing_spellings_remain_raw(self):
        anchor = protected('contact@example.org')
        for tag in ('script', 'style', 'textarea', 'title', 'xmp', 'iframe', 'noscript'):
            document = '<' + tag + '/>' + anchor + '</' + tag + '>'
            with self.subTest(tag=tag):
                self.assertEqual(normalized_html_bytes(document.encode()), document.encode())
        document = '<plaintext>text</plaintext>' + anchor + self.decoder
        self.assertEqual(normalized_html_bytes(document.encode()), document.encode())

    def test_self_closing_spelling_does_not_end_nonvoid_raw_element(self):
        anchor = protected('contact@example.org')
        for tag in ('script', 'style', 'textarea', 'title', 'xmp', 'iframe',
                    'noembed', 'noframes', 'noscript'):
            document = '<' + tag + '/>' + anchor + '</' + tag + '>'
            with self.subTest(tag=tag):
                self.assertEqual(normalized_html_bytes(document.encode()), document.encode())

    def test_decoder_and_beacon_literals_are_not_suppressed(self):
        beacon = '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon="{}"></script>'
        for label, snippet in (('decoder', self.decoder), ('beacon', beacon)):
            contexts = {
                'comment': '<!-- ' + snippet + ' -->',
                'script': '<script>const source = ' + repr(snippet) + ';</script>',
                'style': '<style>p::after{content:' + repr(snippet) + '}</style>',
                'textarea': '<textarea>' + snippet + '</textarea>',
                'title': '<title>' + snippet + '</title>',
                'xmp': '<xmp>' + snippet + '</xmp>',
                'iframe': '<iframe>' + snippet + '</iframe>',
                'noembed': '<noembed>' + snippet + '</noembed>',
                'noframes': '<noframes>' + snippet + '</noframes>',
                'noscript': '<noscript>' + snippet + '</noscript>',
            }
            for context, document in contexts.items():
                with self.subTest(snippet=label, context=context):
                    self.assertEqual(normalized_html_bytes(document.encode()), document.encode())

    def test_unexpected_email_markup_is_preserved(self):
        anchor = protected('contact@example.org')
        cases = [anchor.replace('class=', 'onclick="run()" class='), anchor.replace('class=', 'class="other" class='), anchor.replace('/cdn-cgi/', 'https://example.org/cdn-cgi/'), anchor.replace('[email&#160;protected]', 'changed'), anchor.replace('data-cfemail="', 'data-cfemail="z'), protected('<script>@example.org'), protected('private\n@example.org')]
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(normalized_html_bytes(case.encode()), case.encode())

    def test_unexpected_decoder_scripts_are_preserved(self):
        cases = [self.decoder.replace('</script>', 'run()</script>'), self.decoder.replace('src=', 'type="module" src='), self.decoder.replace('src=', 'src="/unexpected.js" src='), self.decoder.replace('/cdn-cgi/', 'https://example.org/cdn-cgi/'), self.decoder.replace('email-decode.min.js', 'other.js')]
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(normalized_html_bytes(case.encode()), case.encode())

    def test_analytics_and_structured_data(self):
        beacon = '<script type="module" defer src="https://static.cloudflareinsights.com/beacon.min.js/abc" data-cf-beacon="{}"></script>'
        structured = '<script type="application/ld+json">{"name":"Awesome REA"}</script>'
        self.assertEqual(normalized_html_bytes((structured + beacon).encode()), structured.encode())
        for changed in (beacon.replace('module', 'application/ld+json'), beacon.replace('</script>', 'alert(1)</script>'), beacon.replace('type=', 'onclick="run()" type=')):
            self.assertEqual(normalized_html_bytes(changed.encode()), changed.encode())


if __name__ == '__main__':
    unittest.main()

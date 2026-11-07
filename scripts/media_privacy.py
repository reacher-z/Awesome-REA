"""Public-media rules shared by the evidence classifiers, preview fetcher and validators.

Demo screenshots are copied into the published site, so a preview may only point at
content that is public by design. Private attachment hosts and signed query strings
are refused here before a URL reaches data/evidence-previews.json or the deployment.
"""
from __future__ import annotations

import re
import urllib.parse

# GitHub serves access-controlled attachments from this host; the signed URL is the
# only thing that makes one readable, and publishing either would expose private media.
PRIVATE_MEDIA_HOSTS = frozenset({'private-user-images.githubusercontent.com'})
# Signature parameters used by object stores and GitHub's private attachments.
SIGNED_MEDIA_QUERY = re.compile(
    r'(?:^|&)(?:token|jwt|sig|signature|policy|key-pair-id|x-amz-[a-z0-9-]+)=', re.IGNORECASE)


def public_media_url(url: str) -> bool:
    """True for an absolute http(s) media URL that can be published as-is."""
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        return False
    return (parts.scheme in ('http', 'https') and bool(parts.hostname)
            and (parts.hostname or '').lower() not in PRIVATE_MEDIA_HOSTS
            and not SIGNED_MEDIA_QUERY.search(parts.query))

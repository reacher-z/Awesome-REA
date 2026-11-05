"""The site's crawl policy: one list of named crawlers that both robots.txt and its validator use.

Every crawler is already allowed through ``User-agent: *``. A crawler that finds a group naming its own
token obeys only that group and ignores ``*`` (RFC 9309 2.2.1), so each named group repeats the same
allow-all rules; naming the search, AI-search, assistant and training crawlers records that they are
welcome. Product tokens contain only letters, ``-`` and ``_`` (RFC 9309 2.2.1); agents whose names fall
outside that grammar, such as 360Spider or Sogou's spider, are covered by ``*``.

Sources (vendor crawler pages, reviewed 2026-11-05): OpenAI https://developers.openai.com/api/docs/bots,
Anthropic https://support.claude.com/en/articles/8896518, Perplexity
https://docs.perplexity.ai/docs/resources/perplexity-crawlers, Google
https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers, Apple
https://support.apple.com/en-us/119829, Common Crawl https://commoncrawl.org/ccbot, Meta
https://developers.facebook.com/documentation/sharing/webmasters/web-crawlers, Amazon
https://developer.amazon.com/amazonbot, DuckDuckGo
https://duckduckgo.com/duckduckgo-help-pages/results/duckassistbot, Mistral https://docs.mistral.ai/robots,
Microsoft https://www.bing.com/webmasters/help/which-crawlers-does-bing-use-8c184ec0.
"""
from __future__ import annotations

import re

# (comment, product tokens); the order is the order of robots.txt.
CRAWLER_GROUPS = (
    ('Search engines', ('Googlebot', 'bingbot', 'Applebot', 'DuckDuckBot', 'YandexBot', 'Baiduspider',
                        'Bytespider', 'PetalBot', 'Yeti', 'SeznamBot', 'YouBot')),
    ('AI search and answer indexes', ('OAI-SearchBot', 'Claude-SearchBot', 'PerplexityBot', 'Amzn-SearchBot',
                                      'meta-webindexer', 'DuckAssistBot', 'MistralAI-Index', 'Kimi-SearchBot',
                                      'ExaSearchBot', 'YandexAdditional', 'YandexAdditionalBot')),
    ("Assistants and agents fetching on a user's request", ('ChatGPT-User', 'Claude-User', 'Claude-Agent',
                                                            'Perplexity-User', 'Google-Agent', 'Amzn-User',
                                                            'meta-externalfetcher', 'MistralAI-User', 'Kimi-User',
                                                            'ExaUser')),
    ('Model training, research and grounding (Google-Extended and Applebot-Extended are control tokens)',
     ('GPTBot', 'ClaudeBot', 'Google-Extended', 'GoogleOther', 'Google-CloudVertexBot', 'Applebot-Extended',
      'CCBot', 'meta-externalagent', 'Amazonbot', 'MistralAI-Training', 'KimiBot')),
)
CRAWLERS = tuple(token for _, tokens in CRAWLER_GROUPS for token in tokens)
# The crawlers GOAL A6 names; every one must appear above as its own group member.
REQUIRED_AI_CRAWLERS = ('GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-User', 'Claude-SearchBot',
                        'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot-Extended', 'CCBot',
                        'Amazonbot', 'meta-externalagent', 'DuckAssistBot', 'MistralAI-User', 'bingbot', 'Googlebot')
# Content Signals Policy (https://contentsignals.org/): the collection welcomes search, answer engines and
# training. Original editorial content is MIT-licensed; linked works keep their own licenses.
CONTENT_SIGNAL = 'search=yes, ai-input=yes, ai-train=yes'
# IETF draft-kelley-aipref-training-preference-signal-00: Allow states a preference in favour of AI
# training. The * group never matches this token, so it needs its own group.
TRAINING_PREFERENCE_TOKEN = '__usage_ai-training'
TOKEN = re.compile(r'[A-Za-z_-]+')


def robots_txt(site_url: str, sitemap_url: str) -> str:
    """Render the allow-all robots.txt with explicit crawler groups and the sitemap index."""
    site_url = site_url.rstrip('/')
    for token in (*CRAWLERS, TRAINING_PREFERENCE_TOKEN):
        if not TOKEN.fullmatch(token):
            raise ValueError(f'Robots product token outside the RFC 9309 grammar: {token}')
    if len(set(CRAWLERS)) != len(CRAWLERS):
        raise ValueError('A crawler is named twice in robots.txt')
    named = []
    for comment, tokens in CRAWLER_GROUPS:
        named.append(f'# {comment}')
        named.extend(f'User-agent: {token}' for token in tokens)
    return '\n'.join([
        f'# Crawl policy for {site_url}/',
        '# Search engines, AI search, AI assistants and AI training crawlers are all welcome.',
        '# Content Signals Policy: https://contentsignals.org/',
        f'# Agent-readable index: {site_url}/llms.txt',
        '',
        'User-agent: *',
        f'Content-Signal: {CONTENT_SIGNAL}',
        'Allow: /',
        '',
        '# A crawler that matches a named group ignores the * group (RFC 9309 2.2.1),',
        '# so every named group below repeats the same allow-all policy.',
        '# Also covered by *: 360Spider, Sogou spider and other agents outside the RFC 9309 token grammar.',
        '',
        *named,
        f'Content-Signal: {CONTENT_SIGNAL}',
        'Allow: /',
        '',
        '# AI-training usage preference (IETF draft-kelley-aipref-training-preference-signal-00).',
        '# Allow states a preference in favour of AI training. The * group never matches this token.',
        f'User-agent: {TRAINING_PREFERENCE_TOKEN}',
        'Allow: /',
        '',
        f'Sitemap: {sitemap_url}',
        '',
    ])

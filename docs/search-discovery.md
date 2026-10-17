# Search and answer-engine discovery

Reviewed against the linked primary sources on 2026-10-16.

The canonical website is [AwesomeREA.org](https://awesomerea.org/); the public source repository is [reacher-z/Awesome-REA](https://github.com/reacher-z/Awesome-REA). Keep the project identity, website link, and scope consistent. Independent tools and papers in the directory remain their authors' work.

## What the site provides

- `/papers/` and `/zh/papers/` provide the source-reviewed bibliography with original author names, publication status, precise dates, bilingual scope limits and BibTeX downloads. The `.bib` files use standard month macros and are served as `application/x-bibtex; charset=utf-8` through [site/_headers](../site/_headers). Some papers also appear in the curated catalog; the counts are not additive.
- `/resources/` and `/zh/resources/` contain every curated record in ordinary HTML, with its original source, review date, requirements, and a stable section link.
- `/about/` and `/zh/about/` explain the collection, its relationship to REA, source review, and the separate automated repository index.
- `/browse/` and `/zh/browse/` provide category pages for the automated index. Their provenance stays distinct from curated resources.
- Every indexable page has a canonical URL and sitemap entry. Paired language pages have reciprocal `hreflang` links. Fragment IDs locate entries; they are not separate sitemap URLs.
- WebSite, CollectionPage/AboutPage, ItemList, and BreadcrumbList metadata describe the visible content. The site does not claim ratings, official affiliation, or reproduction results it does not have.
- `/llms.txt` is an optional navigation index for readers and tools. `/catalog.json` is the machine-readable curated catalog. Neither guarantees indexing or citation.

Run `python3 scripts/build_production.py` before publication. It validates the source catalogs and generated READMEs, checks the browser script, builds the site, and validates canonical pages, language links, static resource coverage, metadata, and crawler permissions.

## What the evidence supports

| Primary source | Useful finding | Application here |
| --- | --- | --- |
| [Google: AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) | AI search eligibility uses ordinary search requirements. A page must be indexed and eligible for a snippet. No special AI text file or schema is required. | Keep meaningful text and links accessible, provide accurate metadata, and verify indexing in Search Console. |
| [GEO: Generative Engine Optimization](https://arxiv.org/abs/2311.09735) | The experiments study visibility within generative answers and report benefits from some source-backed content edits. The reported gains depend on the experiment and metric. | Use clear explanations and primary evidence. Do not turn the paper's percentage improvements into a traffic or ranking promise. |
| [Generative Engine Optimization: How to Dominate AI Search](https://arxiv.org/abs/2509.08919) | This preprint compares source selection across engines and reports differences in source types, language, freshness, and query phrasing. | Evaluate engines and languages separately. Genuine independent references can complement the project website; copied promotional pages are not independent evidence. |
| [A Critical Survey of GEO, 2023–2026](https://arxiv.org/abs/2607.14035) | This preprint separates discoverability, retrieval, citation, factual use, and traffic, and emphasizes variability and limits of causal claims. | Record repeated observations. Do not call a successful page fetch an index hit or an AI citation. |

The paper notes are a maintenance rationale, not new scientific results from AwesomeREA. The directory's reverse-engineering research entries are separately sourced in the catalog.

## Crawlers

The site's existing `User-agent: *` / `Allow: /` policy permits search crawling, and its robots file declares the sitemap. Check the deployed response as well as the source file; CDN challenges can still prevent a legitimate crawler from reading a page.

[OpenAI documents](https://developers.openai.com/api/docs/bots) that `OAI-SearchBot` serves search while `GPTBot` serves potential model training; their controls are independent. [Perplexity documents](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) its search crawler and verification information. Keep search access and training preferences separate. A request with a crawler-like User-Agent is only a diagnostic request; it does not prove that a genuine crawler has visited or can pass every network control.

## Submission after deployment

1. Confirm that the public canonical homepage, resources, about pages, robots, and sitemap return their intended content. A local build or preview URL is not the production site.
2. In the owner's Google Search Console, verify the `https://awesomerea.org/` property with the issued verification file, keep that file deployed, and submit `https://awesomerea.org/sitemap.xml`.
3. Use URL Inspection for the homepage and a representative resource page. Record the displayed result and any submitted indexing request. A sitemap submission is a discovery hint, not a guarantee of inclusion. [Google sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
4. Bing Webmaster Tools can also accept the sitemap. IndexNow can notify participating engines of changed public URLs after its ownership key is deployed; it does not submit pages to Google or guarantee indexing. [Bing IndexNow guide](https://www.bing.com/indexnow/IndexNowView/IndexNowGetStartedView)

Do not place account emails, dashboard URLs with private identifiers, session cookies, screenshots of account details, or access credentials in this public repository. Search verification files are intended to be publicly reachable ownership proofs; keep the exact issued contents and filename.

## Measurement

Keep a dated private log using the [versioned EN/ZH query set](discovery/queries.v1.json) and [empty observation template](discovery/observation.template.json). The [bilingual observation guide](discovery/README.md) defines provider/version fields, exact-query matching, bounded inspection, distinct failure and citation outcomes, and privacy review before publishing a summary. These files contain no measured results and do not run or schedule searches.

For each observation, record query, language, engine, date, whether web search actually ran, visible source URLs, and whether the cited statement matches the page. Repeat with fixed paraphrases and preserve failures. Record Search Console indexing separately from impressions/clicks and from AI citations. Avoid presenting a single successful answer as durable visibility or a causal effect of these changes.

## AI Can What launch dependency

`aicanwhat.com` is a separate planned directory for AI-built software and agent training/evaluation environments. It should have its own source-backed entries and canonical identity, rather than duplicate the AwesomeREA website. The 2026-10-16 audit could not resolve its hostname; it needs a real deployed site before crawler checks or sitemap submission can establish anything.

At launch, use Games / Websites / Apps as content types, platform and Showcase / Training / Evaluation as separate filters, static entry pages, original evidence, and explicit verification status. Adapt the checks above to that site's actual canonical origin. Submit it as a separate property only after its public URLs work.

## Repeatable IndexNow submission

A top-level `404.html` makes unknown paths return HTTP 404 instead of the homepage. The sitemap omits modification dates when a significant page-change date cannot be established reliably; a source-review timestamp is not a page-modification timestamp.

Run `python3 scripts/submit_indexnow.py` to preview the sitemap URL batch, then `python3 scripts/submit_indexnow.py --submit` after deployment. The command checks the live ownership file, sitemap, public build manifest and canonical page content against this build before sending a notification. It submits only canonical awesomerea.org URLs. HTTP 200 confirms receipt; HTTP 202 means key validation is pending. Neither confirms indexing. See the [IndexNow protocol](https://www.indexnow.org/documentation).

`build-manifest.json` records deterministic hashes and byte sizes for public output files, including the paper bibliography and browser-search projection. It contains no environment paths or account settings. HTML comparison accounts for recognized Cloudflare analytics and email-obfuscation transformations; page text, structured data and application asset revisions remain part of the comparison. Missing or stale canonical pages stop submission even when the sitemap's URL list has not changed.

`site/indexnow.txt` is intentionally public domain-ownership proof, not an account credential. Keep Google verification files and DNS ownership records in place. Search Console account details, DNS dashboard identifiers, credentials and private analytics must never be committed. The GitHub repository is not covered by the website's domain-verification key.

Live-page verification accounts for Cloudflare's recognized analytics injection and email-address obfuscation. It restores only strictly shaped public-email placeholders and removes the matching empty decoder script; changed addresses, unexpected attributes, inline script content and other page changes remain hash-sensitive. This normalization does not change upstream descriptions or disable Cloudflare settings.

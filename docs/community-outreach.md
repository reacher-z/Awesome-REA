# Community outreach

Platform rules reviewed on 2026-10-20 (UTC). Rules change: reread them before every post. Following this checklist does not guarantee that a post is accepted, ranked or kept.

This page covers posting the collection, or news about it, to public communities such as Hacker News and Reddit. Search-engine and answer-engine submission is covered in [search discovery](search-discovery.md).

## Rules checked

| Platform | Official source | What applies to this collection |
| --- | --- | --- |
| Hacker News | [Guidelines](https://news.ycombinator.com/newsguidelines.html) | “Please don't use HN primarily for promotion.” “Please don't put generated text in HN posts. Write your text yourself”, and “please don't automate posting.” “Please don't delete and repost.” “Don't solicit upvotes, comments, or submissions.” Use the original title; “don't editorialize.” In comments: “Don't post generated text or AI-edited text.” |
| Show HN | [Show HN rules](https://news.ycombinator.com/showhn.html) | “Off topic: blog posts, sign-up pages, newsletters, lists, and other reading material. Those can't be tried out, so can't be Show HNs. Make a regular submission instead.” This collection is a list, so it is not a Show HN. “Please don't ask friends to upvote or comment.” |
| Reddit | [Reddit Rules](https://redditinc.com/policies/reddit-rules), Rule 2 | “Abide by community rules. Participate authentically in communities where you have a personal interest, and do not spam or engage in disruptive behaviors (including content manipulation) that interfere with Reddit communities.” Each community also sets its own rules, often including limits on self-promotion. |

Reddit's help-center article on [spam](https://support.reddithelp.com/hc/en-us/articles/360043504051-Spam) refused automated retrieval during this review; read it in a browser before posting there.

## Before posting

1. **Current rules.** Reread the platform rules above and the rules of the specific community, such as a subreddit's sidebar and wiki, and note the date. If they exclude the post, do not post it.
2. **Relevance.** Post only where reverse engineering or the specific subject is on topic. Prefer one concrete item, such as a new case-study collection or a paper directory, over general promotion.
3. **Affiliation.** Say that you maintain or contribute to the collection, in the post or its first comment where the platform allows. Never present your own promotion as an independent recommendation.
4. **Truthful facts.** Take counts from the current [README](../README.md#contents) or `python3 scripts/catalog.py`. Curated entries are source-reviewed, not runtime-tested; scanned repositories are automated README scans; listed tools and papers are their authors' work, and no REA affiliation or official status is implied. Do not invent or inflate traction, such as stars, users, endorsements or coverage.
5. **Duplicates.** Search the platform for earlier submissions of the same URL. Do not repost, delete and repost, or post the same text to several communities.
6. **Votes.** Never ask anyone to upvote, comment or submit. No coordinated voting, extra accounts or booster comments.
7. **Your own words.** Write any title and text yourself. Hacker News rules out generated text in posts and generated or AI-edited text in comments, so no tool or script in this repository drafts submission or comment prose.
8. **Manual posting.** Post by hand from your own account. The repository contains no posting scripts, and none should be added.

## Hacker News handoff

Hacker News submission is a manual decision for the maintainer, not a task for automation or agents. Because the collection is a list, it is not eligible for Show HN; a regular submission is the only option. That submission links the canonical site, `https://awesomerea.org/`, under the homepage's own title, “Awesome Reverse Engineering Anything — Tools, Cases & Papers”, without editorializing. Nobody else prepares submission text, and the maintainer decides whether and when to post.

## Follow-up

- Answer questions as yourself and keep the affiliation disclosure visible.
- Fix any error that commenters find through the usual issue or pull request, not only in a reply.
- When the author of a listed project or paper asks for a correction or removal, open or follow the correction issue and link it from the thread.
- Do not argue with moderation decisions by reposting elsewhere.

## Public tracking

If you record outreach publicly, for example in an issue, keep only the date, platform and community, the URL of the post you intentionally made public, and its publicly visible outcome, such as removed, locked or discussed. Never record account names beyond what the public post already shows, logins, session cookies, tokens, analytics or moderation dashboards, private messages, moderator mail, or other users' personal information. Screenshots follow the same rule.

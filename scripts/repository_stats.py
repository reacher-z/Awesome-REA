"""Star counts for the repositories the site links to.

data/repository-stats.json records them. The production build reads the current counts from GitHub without a
token and hands them to the page builders in a temporary copy named by REA_REPOSITORY_STATS; a read that fails
keeps the recorded number. build_manifest.py leaves the counts out of its hashes, so a plain build_site.py run
still reproduces the deployed manifest.
"""
from __future__ import annotations

from http.client import HTTPException
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RECORDED_PATH = ROOT / 'data/repository-stats.json'
STATS_ENV = 'REA_REPOSITORY_STATS'
READ_TIMEOUT_SECONDS = 5
REPOSITORY = 'reacher-z/Awesome-REA'


def stats_path() -> Path:
    """The counts this build uses: the production build's fresh copy, or the recorded file."""
    return Path(os.environ.get(STATS_ENV) or RECORDED_PATH)


def repository_stars(repository: str = REPOSITORY) -> int | None:
    """A repository's stars from the counts this build uses, or None when it has no count."""
    try:
        stars = json.loads(stats_path().read_text(encoding='utf-8'))['github_stars'][repository]
    except (OSError, KeyError, ValueError, TypeError):
        return None
    return stars if type(stars) is int and stars >= 0 else None


def compact_count(value: int) -> str:
    """1,032 reads 1.0k: rounded, so one more star does not change the bytes of every page."""
    return f'{value / 1000:.1f}k' if value >= 1000 else str(value)


def star_count(repository: str, css_class: str) -> str:
    """A repository's star count; data-stars marks it for build_manifest.py, which leaves it out of the page hashes."""
    stars = repository_stars(repository)
    return f'<span class="{css_class}" data-stars="{repository}">{compact_count(stars)}</span>' if stars is not None else ''


def read_stars(repository: str, *, opener=urlopen) -> int | None:
    """A repository's current star count from the public GitHub API, or None when the read fails."""
    request = Request(f'https://api.github.com/repos/{repository}',
                      headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'awesome-rea-build'})
    try:
        with opener(request, timeout=READ_TIMEOUT_SECONDS) as response:
            stars = json.load(response)['stargazers_count']
    except (OSError, HTTPException, ValueError, KeyError, TypeError):
        return None
    return stars if type(stars) is int and stars >= 0 else None


def refreshed_stats(recorded: dict, *, read=read_stars) -> tuple[dict, int]:
    """The recorded stats with each count replaced by a successful read, and how many reads succeeded."""
    counts = dict(recorded['github_stars'])
    fresh = 0
    for repository in counts:
        stars = read(repository)
        if stars is not None:
            counts[repository] = stars
            fresh += 1
    return {**recorded, 'github_stars': counts}, fresh


def write_fresh_stats(directory: Path) -> tuple[Path, int, int]:
    """Write the refreshed copy into ``directory``; return its path, the reads that succeeded and the total."""
    recorded = json.loads(RECORDED_PATH.read_text(encoding='utf-8'))
    stats, fresh = refreshed_stats(recorded)
    path = Path(directory) / RECORDED_PATH.name
    path.write_text(json.dumps(stats, indent=2) + '\n', encoding='utf-8')
    return path, fresh, len(stats['github_stars'])

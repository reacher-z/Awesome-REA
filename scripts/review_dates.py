"""The shared calendar-date allowance for source-review and inclusion dates."""
import datetime as dt
import re


def review_date_is_future(reviewed, now):
    """Allow tomorrow's UTC date for reviewers whose local calendar is ahead.

    Callers validate the date syntax. Publication dates stay strict, and precise
    review timestamps keep their separate 24-hour comparison.
    """
    return reviewed > now.astimezone(dt.timezone.utc).date() + dt.timedelta(days=1)


def inclusion_date_error(value, now):
    """Check an optional added_at value: the UTC date a record first reached main.

    It shares the review-date allowance for contributors ahead of UTC. It is an
    inclusion date for feeds, never a source-review or publication date.
    """
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return 'use a YYYY-MM-DD calendar date'
    try:
        added = dt.date.fromisoformat(value)
    except ValueError:
        return 'use a YYYY-MM-DD calendar date'
    if review_date_is_future(added, now):
        return 'inclusion date is in the future'
    return None

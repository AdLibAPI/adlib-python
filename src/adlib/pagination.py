"""Cursor pagination. List responses carry ``next_cursor``; pass it back as ``cursor``.
``None`` means last page."""

from __future__ import annotations

from typing import Any, List, Optional

__all__ = ["DEFAULT_MAX_PAGES", "next_cursor", "page_items"]

DEFAULT_MAX_PAGES = 10
"""Every page is a billed call, so iteration stops after 10 pages unless you pass max_pages."""


def next_cursor(page: Any) -> Optional[str]:
    """The ``next_cursor`` of a response, or ``None`` on the last page."""
    if isinstance(page, dict):
        cursor = page.get("next_cursor")
        if isinstance(cursor, str) and cursor:
            return cursor
    return None


def page_items(page: Any) -> List[Any]:
    """The items of a page: ``items`` of a batch job, else ``data``."""
    if isinstance(page, dict):
        items = page.get("items")
        if isinstance(items, list):
            return items
        data = page.get("data")
        if isinstance(data, list):
            return data
    return []


def check_max_pages(max_pages: Optional[int]) -> None:
    if max_pages is not None and (
        isinstance(max_pages, bool) or not isinstance(max_pages, int) or max_pages < 1
    ):
        raise ValueError("max_pages must be a positive integer or None")

from __future__ import annotations

from .rules import ISSUE_KEYWORDS


def classify_promise(title: str, body: str) -> list[str]:
    matches: list[tuple[str, int]] = []
    title_text = title or ""
    body_text = body or ""

    for issue_slug, keywords in ISSUE_KEYWORDS.items():
        match_count = sum(1 for keyword in keywords if keyword in title_text or keyword in body_text)
        if match_count > 0:
            matches.append((issue_slug, match_count))

    matches.sort(key=lambda item: item[1], reverse=True)
    return [issue_slug for issue_slug, _ in matches[:3]]

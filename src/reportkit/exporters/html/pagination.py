import json


class PageNumberStyleResolver:
    """Resolve page numbering into CSS content expressions."""

    @classmethod
    def resolve(cls, format_string):
        """Build CSS content for page counters."""
        parts = []
        remaining = format_string
        while remaining:
            page_index = remaining.find("{page}")
            pages_index = remaining.find("{pages}")
            matches = [(index, token) for index, token in ((page_index, "{page}"), (pages_index, "{pages}")) if index >= 0]
            if not matches:
                parts.append(json.dumps(remaining, ensure_ascii=False))
                break
            index, token = min(matches, key=lambda item: item[0])
            if index:
                parts.append(json.dumps(remaining[:index], ensure_ascii=False))
            parts.append("counter(page)" if token == "{page}" else "counter(pages)")
            remaining = remaining[index + len(token):]
        return " ".join(parts) if parts else '""'

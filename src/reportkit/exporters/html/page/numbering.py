import json


class PageNumberStyleResolver:
    """Resolve page numbering into CSS content expressions."""

    # Page margin boxes do not inherit the body font, so style them explicitly.
    DECLARATIONS = "font-family: Arial, 'Noto Sans Arabic', Tahoma, sans-serif; font-size: 8pt; color: #555555;"

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

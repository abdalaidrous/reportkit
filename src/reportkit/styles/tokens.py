import re
from functools import cache

from ..exporters.html.templates import HtmlTemplateEngine

TOKEN_PATTERN = re.compile(r"(--rk-[\w-]+)\s*:\s*([^;]+);")


@cache
def load_tokens():
    """
    Read the design tokens from tokens.css so every exporter reuses the HTML visual identity.
    """
    raw = dict(TOKEN_PATTERN.findall((HtmlTemplateEngine().static_dir / "tokens.css").read_text(encoding="utf-8")))
    return {name: resolve_token(value.strip(), raw) for name, value in raw.items()}


def resolve_token(value, raw):
    """
    Resolve var(--name) references inside a token value.
    """
    return re.sub(r"var\((--rk-[\w-]+)\)", lambda match: resolve_token(raw[match.group(1)].strip(), raw), value)


def token(name):
    """
    Return one design token value.
    """
    return load_tokens()[name]

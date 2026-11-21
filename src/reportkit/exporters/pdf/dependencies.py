WEASYPRINT_HELP = 'PDF export requires WeasyPrint and its system libraries (Pango). Install it with: pip install "reportkit[pdf]" and see https://doc.courtbouillon.org/weasyprint/stable/first_steps.html'
PYPDF_HELP = 'Chunked PDF export of large reports requires pypdf. Install it with: pip install "reportkit[pdf]"'


def load_weasyprint():
    """
    Import WeasyPrint lazily so it stays an optional dependency, with a clear message when it is missing.
    """
    try:
        import weasyprint
    except (ImportError, OSError) as error:
        raise ImportError(WEASYPRINT_HELP) from error
    return weasyprint


def load_pypdf():
    """
    Import pypdf lazily; it is only needed to merge the chunks of a large report.
    """
    try:
        import pypdf
    except ImportError as error:
        raise ImportError(PYPDF_HELP) from error
    return pypdf

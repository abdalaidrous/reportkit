WEASYPRINT_HELP = 'PDF export requires WeasyPrint and its system libraries (Pango). Install it with: pip install "reportkit[pdf]" and see https://doc.courtbouillon.org/weasyprint/stable/first_steps.html'


def load_weasyprint():
    """
    Import WeasyPrint lazily so it stays an optional dependency, with a clear message when it is missing.
    """
    try:
        import weasyprint
    except (ImportError, OSError) as error:
        raise ImportError(WEASYPRINT_HELP) from error
    return weasyprint

import unicodedata


def text_direction(text):
    """
    Return "ltr" or "rtl" from the first strong character, like dir="auto", or None when the text has none.
    Resolved here because WeasyPrint supports neither dir="auto" nor unicode-bidi: plaintext.
    """
    for character in text or "":
        kind = unicodedata.bidirectional(character)
        if kind == "L":
            return "ltr"
        if kind in ("R", "AL"):
            return "rtl"
    return None

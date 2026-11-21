import re

AUTO_TRACK = 0.6
MIN_COLUMN_CHARACTERS = 12


def distribute(shares, total):
    """
    Turn shares into whole grid columns (at least one each) that add up to the total.
    """
    exact = [share / sum(shares) * total for share in shares]
    widths = [max(1, int(value)) for value in exact]
    for index in sorted(range(len(exact)), key=lambda index: exact[index] - int(exact[index]), reverse=True)[:max(0, total - sum(widths))]:
        widths[index] += 1
    return widths


def track_shares(tracks, content_pixels):
    """
    Convert CSS tracks (fr, auto, %, px) into shares of the width: fixed tracks first, fr tracks share the rest.
    """
    fixed = [fixed_share(track, content_pixels) for track in tracks]
    weights = [0 if share is not None else fraction(track) for track, share in zip(tracks, fixed)]
    rest = max(0.0, 1 - sum(share for share in fixed if share is not None))
    return [share if share is not None else rest * weight / (sum(weights) or 1) for share, weight in zip(fixed, weights)]


def fixed_share(track, content_pixels):
    """
    Return the share of a % or px track, or None for flexible tracks.
    """
    if track.endswith("%"):
        return float(track[:-1]) / 100
    if track.endswith("px"):
        return float(track[:-2]) / content_pixels
    return None


def fraction(track):
    """
    Return the flexible weight of an fr or auto track.
    """
    match = re.fullmatch(r"(\d+(?:\.\d+)?)fr", track)
    return float(match.group(1)) if match else AUTO_TRACK


def column_tracks(columns):
    """
    Return CSS tracks for table columns: declared widths first, the rest weighted by header length like the HTML auto layout.
    """
    return [column.width or f"{max(len(column.title), len(column.subtitle or ''), MIN_COLUMN_CHARACTERS)}fr" for column in columns]

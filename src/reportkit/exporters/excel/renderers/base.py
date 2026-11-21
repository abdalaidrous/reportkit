import re
from dataclasses import dataclass

AUTO_TRACK = 0.6


@dataclass(frozen=True)
class Region:
    """
    Describe where a formatted renderer writes: the top row, the first grid column and the number of grid columns.
    """

    row: int
    column: int
    width: int

    def below(self, rows):
        """
        Return the same region moved down by a number of rows.
        """
        return Region(self.row + rows, self.column, self.width)

    def split(self, shares):
        """
        Split the region into side-by-side slots sized by their shares of the width.
        """
        widths = distribute(shares, self.width)
        return [Region(self.row, self.column + sum(widths[:index]), width) for index, width in enumerate(widths)]


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

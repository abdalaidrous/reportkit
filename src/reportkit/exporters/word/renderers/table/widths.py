from docx.shared import Emu

from .....rendering.tracks import column_tracks, track_shares

EMU_PER_PIXEL = 9525


def get_widths(component, area):
    """
    Share the area width between the table columns: declared widths first, the rest by header length.
    """
    return [Emu(int(area.width * share)) for share in track_shares(column_tracks(component.columns), area.width / EMU_PER_PIXEL)]

#!/usr/bin/env python

"""Flimsy pixel constants locations based on when foscam was first installed.

These depend on camera not moving relative to scene of interest.

"""

# UL = (400, 27) # TEMPLATE IMAGE ROUTINELY GETS FOUND HERE (ABSOLUTE PIXEL COORDS)
# ---------------------------------------------------------------------
# SKINNY GARAGE DOOR PERIMETER RECT
# ULG = (567, 181) => offset: (167, 154) +++ xywh: (167, 154, 52, 112)  # XY relative to template found location
# BRG = (619, 293) => offset: (219, 266)                                # WH is absolute (pixels)
# ---------------------------------------------------------------------
# WHITE-PAINTED TARGET RECT
# ULP = (603, 225) => offset: (203, 198) +++ xywh: (203, 198, 10, 34)  # XY relative to template found location
# BRP = (613, 259) => offset: (213, 232)                                # WH is absolute (pixels)


DOOR_OFFSETXY_WH = (167, 154, 52, 112)
TARG_OFFSETXY_WH = (203, 198, 10, 34)    # offset for where the target was (for flood fill)

_DEFAULT_FOLDER = '/home/pi/Pictures/foscam'
_DEFAULT_TEMPLATE = '/home/pi/Pictures/foscam/template.jpg'
_BASENAME_PATTERN = r'^(?P<day>\d{4}-\d{2}-\d{2})_(?P<hour>\d{2})_(?P<minute>\d{2})_(?P<state>open|close)\.jpg$'

#!/usr/bin/env python

"""Flimsy pixel constants locations based on when foscam was first installed.

These depend on camera not moving relative to scene of interest.

"""
import os
import datetime

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

_cwd = os.path.dirname(os.path.abspath(__file__))
if _cwd.startswith('/home/pi'):
    DEFAULT_FOLDER = '/home/pi/Pictures/foscam'
    DEFAULT_TEMPLATE = '/home/pi/Pictures/foscam/template.jpg'    
elif _cwd.startswith('/Users/ken'):
    DEFAULT_FOLDER = '/Users/ken/Pictures/foscam'
    DEFAULT_TEMPLATE = '/Users/ken/Pictures/foscam/template.jpg'
else:
    DEFAULT_FOLDER = '/home/ken/pictures/foscam'
    DEFAULT_TEMPLATE = '/home/ken/pictures/foscam/template.jpg'

BASENAME_PATTERN = r'^(?P<day>\d{4}-\d{2}-\d{2})_(?P<hour>\d{2})_(?P<minute>\d{2})_(?P<state>open|close)\.jpg$'
DAYONE = datetime.datetime.now() - datetime.timedelta(days=6)

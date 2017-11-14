#!/usr/bin/env python

import os
from dateutil import parser


def parse_image_filename(fname):
    """Parse image filename (just basename) to extract what is stored in the filename itself.
    
    Returns a tuple of (bname, dtm, fsize, state).
    -------
    Output:
    bname -- string for basename
    dtm   -- datetime parsed from image file basename
    fsize -- int number of bytes in image file
    state -- string (open, close, unknown)

    Input argument:
    fname -- string for full path to image file of interest

    """

    # /Users/ken/Pictures/foscam/2017-11-08_06_00_close.jpg

    # get basename
    bname = os.path.basename(fname)
    
    # get file size in bytes
    fsize = os.stat(fname).st_size
    
    # get datetime
    dstr, hh, mm = bname[0:16].split('_')
    dtm = parser.parse(dstr + ' ' + hh + ':' + mm)
    
    # get state
    if 'open' in bname:
        state = 'open'
    elif 'close' in bname:
        state = 'close'
    else:
        state = 'unknown'
    
    return bname, dtm, fsize, state

    
if __name__ == '__main__':
    bname, dtm, fsize, state = parse_image_filename('/Users/ken/Pictures/foscam/2017-11-08_06_00_open.jpg')
    print bname
    print dtm
    print fsize
    print state

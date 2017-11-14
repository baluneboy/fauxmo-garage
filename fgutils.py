#!/usr/bin/env python

import os
import cv2
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


def calc_grayscale_hist(img):
    """calculate histogram from input ASSUMED GRAYSCALE image"""
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    return hist


def plot_hist(hist):
    from matplotlib import pyplot as plt    
    plt.plot(hist)
    plt.xlim([0, 256])
    plt.show()


if __name__ == '__main__':
    
    fname = '/Users/ken/Pictures/foscam/2017-11-08_06_00_open.jpg'
    
    bname, dtm, fsize, state = parse_image_filename(fname)
    print bname
    print dtm
    print fsize
    print state

    from matplotlib import pyplot as plt    
    # FIXME this will actually be our grayscale roi for skinny garage door, sgd
    # read grayscale image from image file
    img = cv2.imread(fname, 0)
    hist = calc_grayscale_hist(img)
    plot_hist(hist)
    
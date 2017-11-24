#!/usr/bin/env python

import os
import re
import cv2
from matplotlib import pyplot as plt

from flimsy_constants import BASENAME_PATTERN, DEFAULT_FOLDER


# TODO compare cv2 to numpy and to matplotlib for histogram calc performance (speed and usage)
def calc_grayscale_hist(img):
    """calculate histogram from input ASSUMED GRAYSCALE image"""
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    return hist


def plot_hist(hist):
    plt.plot(hist)
    plt.xlim([0, 256])
    plt.show()


if __name__ == '__main__':

    from matplotlib import pyplot as plt    
    from foscam import FoscamFile
    
    fname = '/Users/ken/Pictures/foscam/2017-11-08_06_00_open.jpg'
    fs = FoscamFile(fname)
    print fs

    # FIXME this will actually be our grayscale roi for skinny garage door, sgd
    # read grayscale image from image file
    img = cv2.imread(fname, 0)
    hist = calc_grayscale_hist(img)
    plot_hist(hist)

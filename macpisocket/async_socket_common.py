#!/usr/bin/env python

import sys
import numpy as np
from fauxmo_garage.fcimage import FoscamImage
import datetime


def extract_field_value(message, idx_field):
    field = message.split(',')[idx_field]   # gives a string LIKE 'wants:open' or 'wants:close'
    value = field.split(':')[1]  # gives value LIKE 'open' or 'close'
    return field, value


class AnalysisResults(object):
    
    def __init__(self, img_fname):
        self.img_fname = img_fname
        self.fcimage = None
        self.state = None
        self.median = None
        self.elapsed_sec = None
     
    def __str__(self):
        if not self.fcimage: self.compute()
        s = 'state is "%s" because median is %.1f (took %.1f sec)' % (self.state, self.median, self.elapsed_sec)
        return s
        
    def compute(self):
        n1 = datetime.datetime.now()
        self.fcimage = FoscamImage(self.img_fname)
        self.median = np.median(self.fcimage.roi_luminance)
        if self.median < 191.0:
            self.state = 'open'
        else:
            self.state = 'close'
        n2 = datetime.datetime.now()
        self.elapsed_sec = (n2 - n1).total_seconds()
     
     
def demo(state):
    import glob
    fnames = glob.glob('/Users/ken/Pictures/foscam/2017*%s.jpg' % state)
    for fname in fnames:
        ar = AnalysisResults(fname)
        ar.compute()
        if state == ar.state:
            print ar.img_fname, ar.state, ar.median


if __name__ == '__main__':
    demo(sys.argv[1])

#!/usr/bin/env python

import cv2

def show_before_after(img_fname, args, vprint):
    """show side-by-side foscam image before/after analysis with markup on right side"""
    vprint('DISP:', img_fname, 'SEE')
    img = cv2.imread(img_fname, 1)
    cv2.imshow('Hit ESC to close, mouse wheel zoom, right-click for options', img)
    k = cv2.waitKey(0)
    #print k
    if k == 27:  # (linux ESC = 1048603?) wait for ESC key
        print 'user hit ESC'
        cv2.destroyAllWindows()
    elif k == 115:  # (linux S key = 1048691?) wait for 's' key to save and exit
        cv2.imwrite('/tmp/messy.jpg', img)
        print 'wrote /tmp/messy.jpg'
        cv2.destroyAllWindows()
    else:
        print 'unhandled key %d' % k

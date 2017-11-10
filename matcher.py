#!/usr/bin/env python

import cv2
import numpy as np

# UL = (400, 27)
#
# GARAGE RECT
# ULG = (567, 181) => offset: (167, 154) +++ xywh: (167, 154, 52, 112)
# BRG = (619, 293) => offset: (219, 266)
#
# LIGHT-PAINTED RECT
# ULP = (603, 225) => offset: (203, 198) +++ xywh: (203, 198, 10, 34)
# BRP = (613, 259) => offset: (213, 232)
    
DOOR_OFFSETXY_WH = (167, 154, 52, 112)
WPAINT_OFFSETXY_WH = (203, 198, 10, 34)

def get_roi(img, template):

    img2 = img.copy()
    w, h = template.shape[::-1]
    
    # All the 6 methods for comparison in a list
    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED',
                'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    
    # FIXME we only use one for testing for now
    meth = 'cv2.TM_CCOEFF_NORMED'
    method = eval(meth)

    # Apply template Matching
    res = cv2.matchTemplate(img, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    # For this method, we want maximum (NOTE: other methods use minimum)
    top_left = max_loc
    #bottom_right = (top_left[0] + w, top_left[1] + h)

    # draw rectangle around where template was found in target image
    #cv2.rectangle(img, top_left, bottom_right, (0, 0, 255), 2)
    
    # draw rectangle around roi (aka "the garage door")
    #offsetxy_wh = DOOR_OFFSETXY_WH
    #tleft = (top_left[0] + offsetxy_wh[0], top_left[1] + offsetxy_wh[1])
    #bright = (tleft[0] + offsetxy_wh[2], tleft[1] + offsetxy_wh[3])
    #cv2.rectangle(img, tleft, bright, (0, 255, 255), 2)
    
    # histogram equalization on roi
    #roi = img[tleft[1]:bright[1], tleft[0]:bright[0]]
    #img[tleft[1]:bright[1], tleft[0]:bright[0]] = cv2.equalizeHist(roi)

    #print meth, top_left
    
    if False:
        oname = '/tmp/out.jpg'
        # write original and processed side-by-side
        sbs = np.hstack((img, img2)) #stacking images side-by-side
        cv2.imwrite(oname, sbs)
        print 'open -a Firefox file://%s' % oname
        
    return top_left

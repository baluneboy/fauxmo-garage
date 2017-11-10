#!/usr/bin/env python

import cv2
import numpy as np
from matcher import get_roi, DOOR_OFFSETXY_WH, WPAINT_OFFSETXY_WH
from disp import show_before_after

# TODO compare results with histogram equalization on "skinny garage door" vs. clahe
#      EACH of above then does flood_fill (start_px = mid-center of target board)
#      actually look at histograms to get a feel for what those look like

# TODO compare blob detection within "skinny garage door" roi versus flood fill

# FIXME verify that flood fill and/or blob detect is operating only within "skinny garage door"

def flood_fill(img):
    height, width = img.shape[0:2]
    mask = np.zeros((height+2, width+2), np.uint8)
    img2 = img.copy()

    # the starting pixel for the floodFill
    start_pixel = (width/2, height/2)
    
    # maximum distance to start pixel:
    diff = (2, 2, 2)

    retval, im, ma, rect = cv2.floodFill(img2, mask, start_pixel, (0,255,0), diff, diff)

    print retval

    # check the size of the floodfilled area, if its large the door is closed:
    if retval > 11:
        print "garage door closed"
    else:
        print "garage door open"

    return img2

#-----Reading the image-----------------------------------------------------
fname = '/Users/ken/Pictures/foscam/2017-11-08_18_44_open.jpg'
img = cv2.imread(fname, 1)

# read template
tname = '/Users/ken/Pictures/foscam/template.jpg'
template = cv2.imread(tname, 0)

#-----Converting image to LAB Color model----------------------------------- 
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

#-----Splitting the LAB image to different channels-------------------------
l, a, b = cv2.split(lab)
#disp_save_img(l, tag='l')

# use template matching to get roi (aka "the skinny garage door")
top_left = get_roi(l, template)
tleft = (top_left[0] + DOOR_OFFSETXY_WH[0], top_left[1] + DOOR_OFFSETXY_WH[1])
bright = (tleft[0] + DOOR_OFFSETXY_WH[2], tleft[1] + DOOR_OFFSETXY_WH[3])

# histogram equalization on roi
roi = l[tleft[1]:bright[1], tleft[0]:bright[0]]

# use blurring to smooth the roi a bit
bluroi = cv2.GaussianBlur(roi, (7, 7), 0)

#-----Applying CLAHE to L-channel-------------------------------------------
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
#cl = clahe.apply(l)
cl = l.copy()
croi = clahe.apply(bluroi)
#croi_ff = flood_fill(croi)
cl[tleft[1]:bright[1], tleft[0]:bright[0]] = croi
#disp_save_img(cl, tag='cl')

#-----Merge the CLAHE enhanced L-channel with the a and b channel-----------
limg = cv2.merge((cl,a,b))

#-----Converting image from LAB Color model to RGB model--------------------
final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

# draw red rectangle around roi (aka "the skinny garage door")
cv2.rectangle(final, tleft, bright, (0, 0, 255), 2)

# draw green rectangle around subset in roi (aka "the target board")
tleft_targ = (top_left[0] + WPAINT_OFFSETXY_WH[0], top_left[1] + WPAINT_OFFSETXY_WH[1])
bright_targ = (tleft_targ[0] + WPAINT_OFFSETXY_WH[2], tleft_targ[1] + WPAINT_OFFSETXY_WH[3])
cv2.rectangle(final, tleft_targ, bright_targ, (0, 255, 0), 1)

# get a horizontal stack to look at in Firefox
res = np.hstack((img, final))  # stacking images side-by-side

oname = fname.replace('.jpg', '_clahe.jpg')
cv2.imwrite(oname, res)
print 'open -a Firefox file://%s' % oname

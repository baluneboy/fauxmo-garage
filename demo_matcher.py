#!/usr/bin/env python

import cv2
import numpy as np
import matcher
from flimsy_constants import DOOR_OFFSETXY_WH, TARG_OFFSETXY_WH

top_left = (400, 27)  # flimsy constant template typically found here
#print matcher.offsetxy_wh_to_vertices(top_left, DOOR_OFFSETXY_WH)
#print matcher.offsetxy_wh_to_vertices(top_left, TARG_OFFSETXY_WH)

image_fname = '/Users/ken/Pictures/foscam/2017-10-31_15_50_foscam.jpg'
template_fname = '/Users/ken/Pictures/foscam/template.jpg'
output_fname = '/tmp/out.jpg'

img = cv2.imread(image_fname)
tmp = cv2.imread(template_fname)
xywh1 = matcher.match_template(img, tmp)

top_left2, bottom_right2 = matcher.convert_offsetxy_wh_to_vertices(top_left, DOOR_OFFSETXY_WH)
xywh2 = matcher.convert_tleft_bright_to_xywh(top_left2, bottom_right2)

top_left3, bottom_right3 = matcher.convert_offsetxy_wh_to_vertices(top_left, TARG_OFFSETXY_WH)
xywh3 = matcher.convert_tleft_bright_to_xywh(top_left3, bottom_right3)

rectangle_params = [
    (xywh1, (255, 0, 0)),
    (xywh2, (0, 0, 255)),
    (xywh3, (0, 255, 0)),
    ]
print rectangle_params

img2 = matcher.show_markup_image(img, rectangle_params)

# write original and processed side-by-side
sbs = np.hstack((img, img2)) #stacking images side-by-side
cv2.imwrite(output_fname, sbs)
print 'open -a Firefox file://%s' % output_fname

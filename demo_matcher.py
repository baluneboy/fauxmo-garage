#!/usr/bin/env python

import cv2
import numpy as np
from matplotlib import pyplot as plt

import matcher
from flimsy_constants import DOOR_OFFSETXY_WH, TARG_OFFSETXY_WH

top_left = (400, 27)  # flimsy constant template typically found here
#print matcher.offsetxy_wh_to_vertices(top_left, DOOR_OFFSETXY_WH)
#print matcher.offsetxy_wh_to_vertices(top_left, TARG_OFFSETXY_WH)

image_fname = '/Users/ken/Pictures/foscam/2017-11-09_06_07_close.jpg'
template_fname = '/Users/ken/Pictures/foscam/template.jpg'
output_fname = '/tmp/out.jpg'

#img = cv2.imread(image_fname)
#color = ('b','g','r')
#for i,col in enumerate(color):
#    histr = cv2.calcHist([img], [i], None, [256], [0,256])
#    plt.plot(histr,color = col)
#    plt.xlim([0,256])
#plt.show()

img = cv2.imread(image_fname)
# plot the cumulative histogram
n_bins = 256
color = ('b','g','r')
fig, ax = plt.subplots(figsize=(16, 8))

i = 0
c = color[i]
n, bins, patches = ax.hist([img[:,:,i]], n_bins, normed=1, color=c, histtype='step', cumulative=True, label='Color: ' + c)

#ax.hold(True)

i = 1
c = color[i]
n, bins, patches = ax.hist([img[:,:,i]], n_bins, normed=1, color=c, histtype='step', cumulative=True, label='Color: ' + c)

i = 2
c = color[i]
n, bins, patches = ax.hist([img[:,:,i]], n_bins, normed=1, color=c, histtype='step', cumulative=True, label='Color: ' + c)

# tidy up the figure
ax.grid(True)
ax.legend(loc='right')
ax.set_title('Cumulative Step Histograms')
ax.set_xlabel('Pixel [intensity?]')
ax.set_ylabel('Likelihood of Occurrence')

plt.xlim([0,256])
plt.show()

#for i,col in enumerate(color):
#    #print img.shape
#    #print img[:,:,i].shape
#    n, bins, patches = ax.hist([img[:,:,i]], n_bins, normed=1, histtype='step',
#                           cumulative=True, label='Color: ' + col)
#    
#    # tidy up the figure
#    ax.grid(True)
#    ax.legend(loc='right')
#    ax.set_title('Cumulative step histograms')
#    ax.set_xlabel('Annual rainfall (mm)')
#    ax.set_ylabel('Likelihood of occurrence')
#
#    plt.xlim([0,256])
#    plt.show()
    
raise SystemExit

img = cv2.imread(image_fname)
tmp = cv2.imread(template_fname)
xywh1 = matcher.match_template(img, tmp)

top_left2, bottom_right2 = matcher.convert_offsetxy_wh_to_vertices(top_left, DOOR_OFFSETXY_WH)
xywh2 = matcher.convert_vertices_to_xywh(top_left2, bottom_right2)

top_left3, bottom_right3 = matcher.convert_offsetxy_wh_to_vertices(top_left, TARG_OFFSETXY_WH)
xywh3 = matcher.convert_vertices_to_xywh(top_left3, bottom_right3)

rectangle_params = [
    (xywh1, (255, 0, 0)),
    (xywh2, (0, 0, 255)),
    (xywh3, (0, 255, 0)),
    ]
print rectangle_params

img2 = matcher.get_markup_image(img, rectangle_params)

# write original and processed side-by-side
sbs = np.hstack((img, img2)) #stacking images side-by-side
cv2.imwrite(output_fname, sbs)
print 'open -a Firefox file://%s' % output_fname


  


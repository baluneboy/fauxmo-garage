#!/usr/bin/env python

import sys
import cv2
import numpy as np
import matcher
import disp

from matplotlib import pyplot as plt
import matplotlib.mlab as mlab

from flimsy_constants import DOOR_OFFSETXY_WH, TARG_OFFSETXY_WH

# TODO compare results with histogram equalization on "skinny garage door" vs. clahe
#      EACH of above then does flood_fill (start_px = mid-center of target board)
#      actually look at histograms to get a feel for what those look like

# TODO compare blob detection within "skinny garage door" roi versus flood fill

# FIXME verify that flood fill and/or blob detect is operating only within "skinny garage door"

# FIXME change back to LAB (from BGR) nomenclature

def roi_blur_histeq(roi, blursize=7, cliplim=3.0, gridsize=8):
    """Apply blur and histogram equalization to region of interest.
    
    Returns a copy of image (roi) that has been blurred and histogram-equalized.
    -------
    Output:
    roi2 -- output image that has been blurred and hist-equalized

    Input argument:
    roi  -- input image region of interest
    
    Keyword arguments:
    blursize -- int for kernel size of Gaussian blur (x and y same size)
    cliplim  -- float value for CLAHE clipLimit
    gridsize -- int value for CLAHE tileGridSize (x and y same size)

    """
    
    roi2 = roi.copy()
    
    # apply Gaussian blur to smooth the roi [to improve flood-fill results?]
    blur = cv2.GaussianBlur(roi2, (blursize, blursize), 0)
    
    # apply CLAHE to luminance channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    heq_blur = clahe.apply(blur)
    
    return heq_blur
    

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


def main_chain(img_name, tmp_name):
    
    # read input image as 3-channel image
    img = cv2.imread(img_name, 1)
    
    # read template image as gray-scale image
    template = cv2.imread(tmp_name, 0)
    
    # convert image to LAB color model
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    
    # FIXME references to bgr below here should be lab
    
    # split LAB image to 3 channels (L, a, b)
    L, a, b = cv2.split(lab)
    
    # use template matching on luminance channel to find gray-scale template in bigger image
    xywh_template = matcher.match_template(L, template)
    topleft_template = (xywh_template[0], xywh_template[1])
    
    # use flimsy offsetxy_wh of skinny garage door to extract a subset image, roi1
    tleft, bright = matcher.convert_offsetxy_wh_to_vertices(topleft_template, DOOR_OFFSETXY_WH)
    roi1 = L[tleft[1]:bright[1], tleft[0]:bright[0]]  # seems like np arrays have rows/cols swapped???
   
    # FIXME use args for blursize
    # use blurring to smooth skinny garage door (roi1) region a bit
    bluroi1 = cv2.GaussianBlur(roi1, (7, 7), 0)
    
    # FIXME use args for cliplim and gridsize
    # apply CLAHE to roi1 subset of image's luminance channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    croi = clahe.apply(bluroi1)
       
    # TODO flood-fill croi with what start pixel???
    #ffcroi = flood_fill(croi)
    
    # make copy of luminance channel
    c = L.copy()
    
    # replace copy of luminance channel's skinny garage door region with that of the blurred-CLAHE-enhanced version, croi
    c[tleft[1]:bright[1], tleft[0]:bright[0]] = croi
    
    # merge the blurred-CLAHE-enhanced luminance channel back with the a and b channels
    limg = cv2.merge((c, a, b))
    
    # convert image from LAB Color model to BGR
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    # histogram of skinny garage door subset after image processing
    
    colors = ('b',)
    fig, ax = plt.subplots(figsize=(12, 8))    
    
    i = 0
    c = colors[i]
    
    # ith-channel of skinny garage door (roi1) after image processing
    sgd = final[tleft[1]:bright[1], tleft[0]:bright[0]][:,:,i]
    
    intensity_bins = range(0,256)
    n, bins, patches = ax.hist([sgd], intensity_bins, normed=1, color=c, histtype='step', cumulative=True, label='Color: ' + c)
    
    # FIXME we may not always want histogram plot (maybe just during "gather")
    
    # TODO with each image file, always ratchet up a running sum type of histogram OR db each for future summing
    
    # TODO always put percentiles into db table!?
    
    # percentiles
    percs = mlab.prctile([sgd], p=np.arange(10.0, 100.0, 10.0))
    print percs    
    
    # tidy up the figure
    ax.grid(True)
    #ax.legend(loc='right')
    #ax.set_title('Cumulative Step Histograms')
    ax.set_title('Cumulative Step Histogram, Blue Channel, %s' % img_name)
    ax.set_xlabel('Pixel [intensity?]')
    ax.set_ylabel('Likelihood of Occurrence')   
    plt.xlim([0,256])
    
    # save cumulative histogram figure as _chist.jpg
    outname = img_name.replace('.jpg', '_chist.jpg')
    plt.savefig(outname)    
    print 'open -a Firefox file://%s' % outname    

    return img, final, xywh_template


def demo_show_main(img, final, xywh_temp):
    
    topleft_template = (xywh_temp[0], xywh_temp[1])    
    
    topleft2, bottomright2 = matcher.convert_offsetxy_wh_to_vertices(topleft_template, DOOR_OFFSETXY_WH)
    xywh_door = matcher.convert_tleft_bright_to_xywh(topleft2, bottomright2)
    
    topleft3, bottomright3 = matcher.convert_offsetxy_wh_to_vertices(topleft_template, TARG_OFFSETXY_WH)
    xywh_targ = matcher.convert_tleft_bright_to_xywh(topleft3, bottomright3)    
    
    rectangle_params = [
        # xywh   BGRcolor
        (xywh_temp, (255, 0, 0)),
        (xywh_door, (0, 0, 255)),
        (xywh_targ, (0, 255, 0)),
        ]
    
    img2 = matcher.show_markup_image(final, rectangle_params)    
    
    # get a horizontal stack to look at in Firefox
    res = np.hstack((img, img2))  # stacking images side-by-side
    
    oname = '/tmp/out.jpg'
    cv2.imwrite(oname, res)
    print 'open -a Firefox file://%s' % oname    


if __name__ == '__main__':
    #img_name = '/Users/ken/Pictures/foscam/2017-11-08_06_00_open.jpg'
    img_name = sys.argv[1]
    tmp_name = '/Users/ken/Pictures/foscam/template.jpg'
    img, final, xywh_temp = main_chain(img_name, tmp_name)
    if img_name.endswith('close.jpg'):
        img2_name = img_name.replace('close.jpg', 'open.jpg')
    else:
        img2_name = img_name.replace('open.jpg', 'close.jpg')
    img2, final2, xywh_temp2 = main_chain(img2_name, tmp_name)
    
    demo_show_main(img, final, xywh_temp)
#!/usr/bin/env python

import cv2
import numpy as np


def convert_vertices_to_xywh(tleft, bright):
    """Convert two xy-tuples (top_left, bottom_right) to one xywh-tuple.

    Returns 4-tuple of absolute (x, y, w, h) coord pixel values.
    -------
    Output:
    xywh  -- 4-tuple that represents top-left to bottom-right from inputs

    Input arguments:
    tleft    -- 2-tuple:
                (1) absolute x coord (px) of top-left
                (2) absolute y coord (px) of top-left
    bright   -- 2-tuple:
                (1) absolute x coord (px) of bottom-right
                (2) absolute y coord (px) of bottom-right

    """
    x, y = tleft
    w, h = bright[0]-x, bright[1]-y
    return x, y, w, h    


def convert_offsetxy_wh_to_vertices(top_left, offsetxy_wh):
    """Convert (offsetx, offsety, width, height) to two, opposite vertex points.

    Returns 2-tuple of absolute top-left and bottom-right xy coord tuples
    suitable for like cv2.rectangle's pt1 and pt2.
    -------
    Output:
    tleft  -- 2-tuple of top-left absolute coords (xtopleft, ytopleft);       aka pt1
    bright -- 2-tuple of bottom-right absolute coords (xbotright, ybotright); aka pt2

    Input arguments:
    top_left    -- 2-tuple:
                   (1) absolute x coord (px) of top-left
                   (2) absolute y coord (px) of top-left
    offsetxy_wh -- 4-tuple:
                   (1) x offset px relative to absolute xy coords in top_left
                   (2) y offset px relative to absolute xy coords in top_left
                   (3) width in pixels
                   (4) height in pixels

    """
    
    tleft = (top_left[0] + offsetxy_wh[0], top_left[1] + offsetxy_wh[1])
    bright = (tleft[0] + offsetxy_wh[2], tleft[1] + offsetxy_wh[3])
    return tleft, bright


def match_template(img, template):
    """Match a subset image (template) within the input image (img).
    
    Returns tuple (x, y, w, h) for pixel values where template was best matched in img.
    -------
    Output:
    found_xywh -- 4-tuple of pixel values:
                  (1) x coord where top_left of template was found in img
                  (1) y coord where top_left of template was found in img
                  (3) width of template
                  (4) height of template

    Input arguments:
    img      -- input image we search for template
    template -- template image used for searching in img

    """
    print type(img)
    print type(template)
    h, w = template.shape[0:2]  # FIXME does this work for all cv2's
    
    # TODO use large collection of images to find which method works best (maybe some better in dark?)
    # TODO some methods use max_loc while others use min_loc for where template best matches
    # TODO there is a 7th method that we discarded for poor performance early on
    #methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    #
    # TODO to iterate through list of methods for testing, use following:
    #for meth in methods:
    #    method = eval(meth)

    # apply template matching
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    # for this method, we want maximum, max_loc (NOTE: other methods use minimum, min_loc)
    found_xywh = max_loc + (w, h)

    return found_xywh


def get_markup_image(img, rect_params):
    """Draw a rectangle around region(s) of interest within input image.
    
    Returns markup image (copy of img) with rectangles drawn around each region using rect_params.
    -------
    Output:
    img2 -- output markup image (a copy of img)
    
    Input arguments:
    img  -- input image that we copy and annotate
    rect_params -- list of 2-tuples, (xywh, BGRcolor), one tuple for each rectangle
    
    """

    img2 = img.copy()

    for xywh, color in rect_params:
        # draw rectangle around where template was found in target image
        top_left = (xywh[0], xywh[1])
        bottom_right = (top_left[0] + xywh[2], top_left[1] + xywh[3])
        cv2.rectangle(img2, top_left, bottom_right, color, 2)
    
    return img2

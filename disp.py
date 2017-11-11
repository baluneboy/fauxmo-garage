#!/usr/bin/env python

import cv2

def show_before_after(img_fname, args, vprint):
    """show side-by-side foscam image before/after analysis with markup on right side"""
    vprint('DISP:', img_fname, 'SEE')

    top_left = (x1, y1)    
    xywh1 = (x1, y1, w1, h1)

    top_left2, bottom_right2 = matcher.convert_offsetxy_wh_to_vertices(top_left, DOOR_OFFSETXY_WH)
    xywh2 = matcher.convert_tleft_bright_to_xywh(top_left2, bottom_right2)
    
    top_left3, bottom_right3 = matcher.convert_offsetxy_wh_to_vertices(top_left, TARG_OFFSETXY_WH)
    xywh3 = matcher.convert_tleft_bright_to_xywh(top_left3, bottom_right3)    
    
    rectangle_params = [
        # xywh   BGRcolor
        (xywh1, (255, 0, 0)),
        (xywh2, (0, 0, 255)),
        (xywh3, (0, 255, 0)),
        ]
    
    img2 = matcher.show_markup_image(final, rectangle_params)    
    
    # get a horizontal stack to look at in Firefox
    res = np.hstack((img, img2))  # stacking images side-by-side
    
    oname = fname.replace('.jpg', '_clahe.jpg')
    cv2.imwrite(oname, res)
    print 'open -a Firefox file://%s' % oname
#!/usr/bin/env python

"""Use a webcam as a sensor to control a garage door.

This module provides classes to try determine whether the garage door is open.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

"""

import os
import cv2
import random
import numpy as np
from dateutil import parser

from pims.utils.datetime_ranger import DateRange

import matcher
from flimsy_constants import DOOR_OFFSETXY_WH
from fgutils import calc_grayscale_hist, plot_hist


class FoscamFile(object):
    
    """A webcam filename parser.

    Attributes are documented inline with the attribute's declaration (see __init__ method below).

    Properties created with the @property decorator are documented in the property's getter method.

    """
    
    def __init__(self, filename):
        """Initialize FoscamFile object.
        
        Args:
            filename (str): Full path filename for input image file of interest.

        """        
        self.filename = filename
        self.bname = None
        self.fsize = None  #: list of str: Doc comment *before* attribute, with type specified
        self.dtm = None
        self.state = None
        
        # get actual values for bname, fsize, dtm and state from filename
        self.parse_image_filename()
        
    def __str__(self):
        s =  '%s says "door %s" at %s (%d bytes)' % (self.bname, self.state, self.dtm, self.fsize)
        return s
            
    def parse_image_filename(self):
        """Parse image filename (just basename) to extract what is stored in the filename itself.
        
        Returns a tuple of (bname, dtm, fsize, state).
        -------
        Output:
        bname -- string for basename
        dtm   -- datetime parsed from image file basename
        fsize -- int number of bytes in image file
        state -- string (open, close, unknown)
    
        """
    
        # /Users/ken/Pictures/foscam/2017-11-08_06_00_close.jpg
    
        # get basename
        self.bname = os.path.basename(self.filename)
        
        # get file size in bytes
        self.fsize = os.stat(self.filename).st_size
        
        # get datetime
        dstr, hh, mm = self.bname[0:16].split('_')
        self.dtm = parser.parse(dstr + ' ' + hh + ':' + mm)
        
        # get state
        if 'open' in self.bname:
            state = 'open'
        elif 'close' in self.bname:
            state = 'close'
        else:
            state = 'unknown'
        self.state = state


class FoscamImage(object):
    
    """A webcam image.

    Attributes are documented inline with the attribute's declaration (see __init__ method below).

    Properties created with the @property decorator are documented in the property's getter method.

    """
    
    def __init__(self, img_name, tmp_name='/Users/ken/Pictures/foscam/template.jpg'):
        self.img_name = img_name
        self.tmp_name = tmp_name
        self.foscam_file = FoscamFile(self.img_name)
        self._image = None
        self._template = None
        self._lab = None
        self._xywh_template = None
        self._roi_vertices = None
        self._processed_image = None
        self._roi_lum = None

    def __str__(self):
        s =  '%s' % self.foscam_file
        return s

    @property
    def image(self):
        """numpy.ndarray: Array (h, w, 3) of input image of interest; 3rd dimension is color."""
        if self._image:
            return self._image
        return cv2.imread(self.img_name, 1)

    @property
    def roi_lum(self):
        """numpy.ndarray: Array (h, w) of luminance channel of roi from processed image."""
        if self._roi_lum:
            return self._roi_lum
        topleft, botright = self.roi_vertices
        _roi = self.processed_image[topleft[1]:botright[1], topleft[0]:botright[0]]
        _lab_roi = cv2.cvtColor(_roi, cv2.COLOR_BGR2LAB)  # convert color image to LAB color model
        L, a, b = cv2.split(_lab_roi)  # split LAB image to 3 channels (L, a, b); L is luminance channel
        return L
    
    @property
    def template(self):
        """numpy.ndarray: Array (h, w) of template image (grayscale)"""
        if self._template:
            return self._template
        return cv2.imread(self.tmp_name, 0)

    @property
    def lab(self):
        """Get the image as LAB color model in 3-channel tuple (L, a, b)."""
        if self._lab:
            return self._lab
        lab = cv2.cvtColor(self.image, cv2.COLOR_BGR2LAB)  # convert color image to LAB color model
        L, a, b = cv2.split(lab)  # split LAB image to 3 channels (L, a, b); L is luminance channel
        return L, a, b

    @property
    def xywh_template(self):
        """Get xywh-tuple for where the template was found in the image."""
        if self._xywh_template:
            return self._xywh_template
        L = self.lab[0]  # luminance channel is first element of the lab tuple
        xywh_template = matcher.match_template(L, self.template)  # both inputs are grayscale
        return xywh_template

    @property
    def roi_vertices(self):
        """Get the (top-left, bottom-right) vertices of where roi was found in the image."""
        if self._roi_vertices:
            return self._roi_vertices
        
        # use template matching on luminance channel to find gray-scale template in image of interest
        topleft_template = (self.xywh_template[0], self.xywh_template[1])
        
        # FIXME what if foscam moves, then offset method will not work robustly, will it?
        # extract skinny garage door subset image (roi1) using flimsy offsetxy_wh method
        topleft_roi, botright_roi = matcher.convert_offsetxy_wh_to_vertices(topleft_template, DOOR_OFFSETXY_WH)
        
        return topleft_roi, botright_roi
    
    @property
    def processed_image(self):
        """Get the final, processed image."""
        if self._processed_image:
            return self._processed_image
        return self.apply_blur_and_clahe(blursize=5, cliplim=3.0, gridsize=8)
    
    def apply_blur_and_clahe(self, blursize=5, cliplim=3.0, gridsize=8):
        """Apply Gaussian blur and histogram equalization CLAHE to a region of interest (roi).
        
        Returns a final image with roi that has been blurred and histogram-equalized via CLAHE.
        -------
        Output:
        final -- processed copy of input image where roi has been replaced with blurred CLAHE
        xywh_template -- xywh-tuple where template image was found in img
        topleft_roi -- top-left xy-tuple of coords where skinny garage door (offset from template) WAS ASSUMED
        botright_roi -- bottom-right xy-tuple of coords where skinny garage door (offset from template) WAS ASSUMED    
    
        Input argument:
        img_name -- string for full path to image of interest
        template_name -- string for full path to template image
        
        Keyword arguments:
        blursize -- int for kernel size of Gaussian blur (x and y same size); None to skip blurring
        cliplim  -- float value for CLAHE clipLimit
        gridsize -- int value for CLAHE tileGridSize (x and y same size)
    
        """
               
        # get explicit channels from our LAB color model split into 3 channels (L, a, b)
        L, a, b = self.lab
        
        # use template matching on luminance channel to find gray-scale template in image of interest (roi is skinny garage door)
        topleft_roi, botright_roi = self.roi_vertices
        roi1 = L[topleft_roi[1]:botright_roi[1], topleft_roi[0]:botright_roi[0]]  # looks like np arrays have rows/cols swapped
    
        if blursize:   
            # use blurring to smooth skinny garage door (roi1) region a bit
            roi2 = cv2.GaussianBlur(roi1, (blursize, blursize), 0)
        else:
            # skip blurring
            roi2 = roi1
        
        # apply CLAHE to skinny garage door (roi2 may/not be blurred) subset of image's luminance channel
        clahe = cv2.createCLAHE(clipLimit=cliplim, tileGridSize=(gridsize, gridsize))
        roi3 = clahe.apply(roi2)
        
        # replace copy of luminance channel's skinny garage door region with that of the blurred-CLAHE-enhanced version, roi3
        L[topleft_roi[1]:botright_roi[1], topleft_roi[0]:botright_roi[0]] = roi3
        
        # merge the blurred-CLAHE-enhanced luminance channel back with the a and b channels
        limg = cv2.merge((L, a, b))
        
        # convert image from LAB Color model to BGR
        final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        return final

    def get_hist(self):
        return calc_grayscale_hist(self.roi_lum)

    def plot_hist(self):
        h = self.get_hist()
        plot_hist(h)
        
    def show_results(self):
        
        # get xywh-tuple from top-left and bottom-right vertices of skinny garage door
        xywh_door = matcher.convert_vertices_to_xywh(*self.roi_vertices)
     
        # tuple of parameters for rectangles to draw
        rectangle_params = [
            # xywh                color:  B    G    R
            (self.xywh_template,       (255,   0,   0)),
            (xywh_door,                (0,     0, 255)),
            ]
        
        # get markup of processed image: blue rectangle around template, red around skinny garage door
        img2 = matcher.get_markup_image(fci.processed_image, rectangle_params)    
        
        # get a horizontal stack result image to look at in Firefox
        res = np.hstack((fci.image, img2))  # stacking images side-by-side
        
        oname = '/tmp/out.jpg'
        cv2.imwrite(oname, res)
        print 'open -a Firefox file://%s' % oname


class Deck(object):

    def __init__(self, date_range=None, morning=True, state=None, tmp_name=None, verbose=False):
        self._date_range = date_range  # FIXME use a setter to enforce isinstance of DateRange
        self._set_morning(morning)
        self._set_state(state)
        self._set_tmp_name(tmp_name)   # FIXME setter: None means get from constants; otherwise, just check os.path.exists
        self._set_verbose(verbose)     # FIXME setter: see _set_morning
        self._filenames = None
        self._images = None

    def __len__(self):
        return len(self.images)

    @property
    def date_range(self):
        """DateRange: an object with start date and stop date attributes."""
        if self._date_range:
            return self._date_range
        return DateRange(8, 2)

    @property
    def morning(self):
        """boolean: True for just morning files; False for all files"""
        return self._morning
    
    def _set_morning(self, value):
        if not isinstance(value, bool):
            raise TypeError('Deck.morning must be a bool')
        self._morning = value

    @property
    def state(self):
        """string: state of door indicated in filename (open or close); None for don't care"""
        return self._state
    
    def _set_state(self, value):
        if value:
            if value not in ['open', 'close']:
                raise TypeError('Deck.state should be either open or close')        
        self._state = value
        
    @property
    def filenames(self):
        """Get list of filenames."""
        if self._filenames:
            return self._filenames
        
        # TODO use inputs to build list of image filenames based on: date, am/pm, state
        _filenames = ['/Users/ken/Pictures/foscam/2017-11-08_06_00_open.jpg',
            '/Users/ken/Pictures/foscam/2017-11-08_06_00_close.jpg']
                
        return _filenames

    @property
    def images(self):
        """Get list of images."""
        if self._images:
            return self._images

        _images = []
        for img_name in self.filenames:        
            if self.tmp_name:
                _images.append(FoscamImage(img_name, tmp_name=self.tmp_name))
            else:
                _images.append(FoscamImage(img_name))
                
        return _images
    
    def random_draw(self):
        fcimage = random.choice(self.images)
        return fcimage
    
    def compare_pairs(self):
        # TODO for each 'close' in images (use FoscamFile attributes)
        #      verify we have pairing, then overlay roi_lum_histograms on one plot
        pass
    
    
if __name__ == '__main__':
    
    deck = Deck(state='open')
    print deck.date_range
    print deck.state
    #for fci in deck.images:
    #    print fci
    #    #fci.show_results()
    #    print fci.roi_lum.shape
    #    fci.plot_hist()

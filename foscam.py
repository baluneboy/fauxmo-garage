#!/usr/bin/env python

"""Use a webcam as a sensor to control a garage door.

This module provides classes to try determine whether the garage door is open.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

"""

import os
import re
import cv2
import numpy as np
from dateutil import parser

from pims.files.filter_pipeline import FileFilterPipeline

import matcher
from template import GrayscaleTemplateImage
from flimsy_constants import DOOR_OFFSETXY_WH, DEFAULT_TEMPLATE
from flimsy_constants import DEFAULT_FOLDER, BASENAME_PATTERN
from fgutils import calc_grayscale_hist, plot_hist


def parse_foscam_fullfilestr(fullfilestr, bname_pattern=BASENAME_PATTERN):
    """convert foscam timestamped fullfile string to datetime object"""
    # /Users/ken/Pictures/foscam/2017-11-08_06_00_close.jpg
    dtm = None
    state = None
    bname = os.path.basename(fullfilestr)
    if not re.match(bname_pattern, bname):
        pass
    else:
        p = re.compile(bname_pattern)
        m = p.search(bname)
        daystr = m.group('day')
        hh = m.group('hour')
        mm = m.group('minute')
        state = m.group('state')
        dtm = parser.parse(daystr + ' ' + hh + ':' + mm)
    return dtm, state


def get_date_range_foscam_files(start, stop, morning=True, state=None, topdir=DEFAULT_FOLDER):
    # Initialize processing pipeline (prime the pipe with callables)
    ffp = FileFilterPipeline(
        DateRangeStateFoscamFile(start, stop, morning=morning, state=state),
        # YoungFile(max_age_minutes=max_age_minutes),
    )

    # get all files [quickly?]
    file_list = [os.path.join(topdir, f) for f in os.listdir(topdir) if os.path.isfile(os.path.join(topdir, f))]

    # apply processing pipeline to probably prune input list of files
    my_files = []
    for f in ffp(file_list):
        my_files.append(f)

    return my_files


class DateRangeStateFoscamFile(object):
    
    def __init__(self, start, stop, morning=True, state=None):
        self.start = start  # a datetime.date object
        self.stop = stop    # a datetime.date object
        self.morning = morning
        self.state = state
        
    def __call__(self, file_list):
        for f in file_list:
            try:
                fdtm, fstate = parse_foscam_fullfilestr(f)
            except:
                fdtm, fstate = None, None
            keep = False
            state_matches = False
            if self.state:
                state_matches = self.state == fstate
            else:
                state_matches = True
            if fdtm:  # not None
                if state_matches:
                    # if fdtm.date() >= self.start and fdtm.date() <= self.stop:
                    if self.start <= fdtm.date() <= self.stop:
                        if self.morning:
                            if fdtm.hour < 12:
                                keep = True
                        else:
                            keep = True
            if keep:
                yield f
                
    def __str__(self):
        return 'is a Foscam image file with %s < fname date < %s' % (self.start, self.stop)


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
        self.bname = None  #: str: image file basename
        self.fsize = None  #: int: bytes from os.stat's st_size
        self.dtm = None    #: datetime: parsed from filename
        self.state = None  #: str: door open/closed/unknonwn parsed from filename
        
        # now get actual values for attributes
        self.parse_image_filename()
        
    def __str__(self):
        s =  '%s has state: "door %s" at %s (%d bytes)' % (self.bname, self.state, self.dtm, self.fsize)
        return s
            
    def parse_image_filename(self):
        """Parse image filename to extract some useful info.
        
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
        
        # get datetime and state
        self.dtm, self.state = parse_foscam_fullfilestr(self.filename)

    
class FoscamImage(object):
    
    """A webcam image object.

    Attributes are documented inline with the attribute's declaration (see __init__ method below).

    Properties created with the @property decorator are documented in the property's getter method.

    """

    def __init__(self, img_name, template=DEFAULT_TEMPLATE):
        self.img_name = img_name
        self.foscam_file = FoscamFile(self.img_name)
        self._template = template
        self._image = None
        self._lab = None
        self._xywh_template = None
        self._roi_vertices = None
        self._processed_image = None
        self._roi_luminance = None

    def __str__(self):
        s = '%s' % self.foscam_file
        return s

    @property
    def image(self):
        """numpy.ndarray: Array (h, w, 3) of input image of interest; 3rd dimension is color."""
        if self._image:
            return self._image
        return cv2.imread(self.img_name, 1)

    @property
    def roi_luminance(self):
        """numpy.ndarray: Array (h, w) of luminance channel of roi from processed image."""
        if self._roi_luminance:
            return self._roi_luminance
        topleft, botright = self.roi_vertices
        _roi = self.processed_image[topleft[1]:botright[1], topleft[0]:botright[0]]
        _lab_roi = cv2.cvtColor(_roi, cv2.COLOR_BGR2LAB)  # convert color image to LAB color model
        L, a, b = cv2.split(_lab_roi)  # split LAB image to 3 channels (L, a, b); L is luminance channel
        return L

    @property
    def template(self):
        """numpy.ndarray: Array (h, w) of template image (grayscale)"""
        if self._template is None:
            # is None, so use default template
            template = GrayscaleTemplateImage(DEFAULT_TEMPLATE)
            return template.image

        elif isinstance(self._template, np.ndarray):
                # type is numpy array, so return as-is
                return self._template

        elif isinstance(self._template, GrayscaleTemplateImage):
                # type is GrayscaleTemplateImage, so return image part
                return self._template.image

        elif isinstance(self._template, str):
            # type is str, so read from string filename
            template = GrayscaleTemplateImage(self._template)
            return template.image

        else:
            raise TypeError('template is unexpected type %s' % type(self._template))

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
        return calc_grayscale_hist(self.roi_luminance)

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

        oname = '/template/out.jpg'
        cv2.imwrite(oname, res)
        print 'open -a Firefox file://%s' % oname
        self.img_name = img_name
        self.foscam_file = FoscamFile(self.img_name)
        self._template = template
        self._tmp_name = None
        self._image = None
        self._template = None
        self._lab = None
        self._xywh_template = None
        self._roi_vertices = None
        self._processed_image = None
        self._roi_luminance = None

    def __str__(self):
        s = '%s' % self.foscam_file
        return s

    @property
    def image(self):
        """numpy.ndarray: Array (h, w, 3) of input image of interest; 3rd dimension is color."""
        if self._image:
            return self._image
        return cv2.imread(self.img_name, 1)

    @property
    def roi_luminance(self):
        """numpy.ndarray: Array (h, w) of luminance channel of roi from processed image."""
        if self._roi_luminance is None:
            topleft, botright = self.roi_vertices
            _roi = self.processed_image[topleft[1]:botright[1], topleft[0]:botright[0]]
            _lab_roi = cv2.cvtColor(_roi, cv2.COLOR_BGR2LAB)  # convert color image to LAB color model
            L, a, b = cv2.split(_lab_roi)  # split LAB image to 3 channels (L, a, b); L is luminance channel
            return L
        return self._roi_luminance

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
        return calc_grayscale_hist(self.roi_luminance)

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


if __name__ == '__main__':

    import datetime
    import pandas as pd
    from deck import Deck
    
    #start = datetime.datetime(2017, 11, 20).date()
    #stop = datetime.datetime(2017, 11, 21).date()
    #files = get_date_range_foscam_files(start, stop, morning=False, state=None, topdir=DEFAULT_FOLDER)
    #print len(files)

    # # d1 = datetime.datetime(2017, 11,  4).date()
    d1 = datetime.datetime(2017, 11, 20).date()
    d2 = datetime.datetime(2017, 11, 21).date()
    dr = pd.date_range(d1, d2)
    state = None
    morning = False
    deck = Deck(date_range=dr, state=state, morning=morning)
    #deck.overlay_roi_histograms()
    deck.show_roi_luminance_medians()
    #
    # raise SystemExit
    
    #print deck.daterange
    #print deck.state
    #print deck.morning
    #print deck.state
    #print deck.tmp_name
    #print deck.verbose
    #print deck.filenames, len(deck)
    #print deck.images
    # if len(deck.images) > 6:
    #     print 'more than 6, so only look at first 6'
    # for fci in deck.images[:6]:
    #     print fci.foscam_file.filename
    #     #fci.show_results()
    #     #print fci.roi_luminance.shape
    #     fci.plot_hist()
    pass

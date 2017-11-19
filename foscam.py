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
import random
import datetime
import numpy as np
from dateutil import parser
from matplotlib import pyplot as plt

#from pims.utils.daterange import daterange
from pims.utils.datetime_ranger import DateRange
from pims.files.filter_pipeline import FileFilterPipeline

import matcher
from flimsy_constants import DOOR_OFFSETXY_WH, _DEFAULT_FOLDER, _DEFAULT_TEMPLATE, _BASENAME_PATTERN
from fgutils import calc_grayscale_hist, plot_hist


def parse_foscam_fullfilestr(fullfilestr, bname_pattern=_BASENAME_PATTERN):
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


def get_date_range_foscam_files(start, stop, morning=True, state=None, topdir=_DEFAULT_FOLDER):
   
    # Initialize processing pipeline (prime the pipe with callables)
    ffp = FileFilterPipeline(
        DateRangeStateFoscamFile(start, stop, morning=morning, state=state),
        #YoungFile(max_age_minutes=max_age_minutes),
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
        self.start = start
        self.stop = stop
        self.morning = morning
        self.state = state
        
    def __call__(self, file_list):
        for f in file_list:
            fdtm, fstate = parse_foscam_fullfilestr(f)
            keep = False
            state_matches = False
            if self.state:
                state_matches = self.state == fstate
            else:
                state_matches = True
            if fdtm:  # not None
                if state_matches:
                    if fdtm.date() >= self.start and fdtm.date() <= self.stop:
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
        s =  '%s says "door %s" at %s (%d bytes)' % (self.bname, self.state, self.dtm, self.fsize)
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
    
    """A webcam image.

    Attributes are documented inline with the attribute's declaration (see __init__ method below).

    Properties created with the @property decorator are documented in the property's getter method.

    """
    
    def __init__(self, img_name, tmp_name=_DEFAULT_TEMPLATE):
        self.img_name = img_name
        self.tmp_name = tmp_name
        self.foscam_file = FoscamFile(self.img_name)
        self._image = None
        self._template = None
        self._lab = None
        self._xywh_template = None
        self._roi_vertices = None
        self._processed_image = None
        self._roi_luminance = None

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


class Deck(object):

    def __init__(self, basedir=_DEFAULT_FOLDER, daterange=None, morning=True, state=None, tmp_name=None, verbose=False):
        self._set_basedir(basedir)
        self._set_daterange(daterange)
        self._set_morning(morning)
        self._set_state(state)
        self._set_tmp_name(tmp_name)
        self._set_verbose(verbose)
        self._images = None

    def __len__(self):
        return len(self.images)

    @property
    def basedir(self):
        """str: string for base directory where image files are stored"""
        return self._basedir

    def _set_basedir(self, value):
        if not value:
            if not os.path.exists(value):
                raise ValueError('"%s" does not exist as foscam image folder' % f)
        self._basedir = value

    @property
    def daterange(self):
        """DateRange: an object to keep start and stop dates"""
        return self._daterange

    def _set_daterange(self, value):
        if not value:
            value = DateRange(8, 2)
        self._daterange = value

    @property
    def morning(self):
        """boolean: True for just morning files; False for all files"""
        return self._morning
    
    def _set_morning(self, value):
        if not isinstance(value, bool):
            raise TypeError('Deck.morning must be a bool')
        self._morning = value

    @property
    def verbose(self):
        """boolean: True for being more verbose"""
        return self._verbose
    
    def _set_verbose(self, value):
        if not isinstance(value, bool):
            raise TypeError('Deck.verbose must be a bool')
        self._verbose = value

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
    def tmp_name(self):
        """string: full filename for template image; None to get from constants"""
        return self._tmp_name
    
    def _set_tmp_name(self, value):
        if value:
            if not os.path.exists(value):
                raise TypeError('Deck.tmp_name template file "%s" does not exist' % value)
        else:
            value = _DEFAULT_TEMPLATE
        self._tmp_name = value

    def _get_filenames(self):
        """get list of filenames"""
        _filenames = get_date_range_foscam_files(self.daterange.start, self.daterange.stop, morning=self.morning)
        if self.state:           
            [ _filenames.remove(f) for f in _filenames if self.state not in f ]
        return _filenames

    @property
    def images(self):
        """Get list of images."""
        if self._images:
            return self._images

        _images = []
        fnames = self._get_filenames()
        for img_name in fnames:
            if self.tmp_name:
                _images.append(FoscamImage(img_name, tmp_name=self.tmp_name))
            else:
                _images.append(FoscamImage(img_name))
                
        return _images
    
    def random_draw(self):
        fcimage = random.choice(self.images)
        return fcimage
    
    def overlay_roi_histograms(self):
        h0 = self.images[0].get_hist()
        hopen = np.zeros_like(h0)
        hclose = np.zeros_like(h0)        
        for fci in self.images[1:]:
            if 'open' in os.path.basename(fci.foscam_file.filename):
                hopen += fci.get_hist()
            else:
                hclose += fci.get_hist()
        #    plt.plot(h, color=c, alpha=0.6)
        #    print fci.foscam_file.filename, type(h)
        #plt.xlim([0, 256])
        #plt.show()    
        plt.plot(hopen, 'r')
        plt.plot(hclose, 'b')
        plt.xlim([0, 256])
        plt.show()
    
    def show_roi_luminance_medians(self):
        for fci in self.images:
            med = np.median(fci.roi_luminance)
            if med < 191.0:
                guess = 'open'
            else:
                guess = 'close'
            if not fci.foscam_file.state == guess:
                print 'open -a Firefox file://%s # OOPS!' % fci.img_name


if __name__ == '__main__':

    d1 = datetime.datetime(2015, 11,  4).date()
    d2 = datetime.datetime(2017, 11, 17).date()
    dr = DateRange(d1, d2)
    state = None
    morning = False
    deck = Deck(daterange=dr, state=state, morning=morning)
    #deck.overlay_roi_histograms()
    deck.show_roi_luminance_medians()
    
    raise SystemExit
    
    #print deck.daterange
    #print deck.state
    #print deck.morning
    #print deck.state
    #print deck.tmp_name
    #print deck.verbose
    #print deck.filenames, len(deck)
    #print deck.images
    if len(deck.images) > 6:
        print 'more than 6, so only look at first 6'
    for fci in deck.images[:6]:
        print fci.foscam_file.filename
        #fci.show_results()
        #print fci.roi_luminance.shape
        fci.plot_hist()

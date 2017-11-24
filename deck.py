#!/usr/bin/env python

"""A deck (collection) of webcam images for ensemble analysis.

This module provides a class for analysis of a collection of images.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

"""

import os
import random
import datetime
import numpy as np
from matplotlib import pyplot as plt

# from pims.utils.datetime_ranger import DateRange
import pandas as pd

from template import GrayscaleTemplateImage
from foscam import FoscamImage, get_date_range_foscam_files
from flimsy_constants import DEFAULT_FOLDER, DEFAULT_TEMPLATE, DAYONE


class FoscamImageIterator(object):

    def __init__(self, filenames, tmp=DEFAULT_TEMPLATE):
        self.filenames = filenames
        self._tmp = tmp
        self._tmp_name = None
        self._template = None
        self.current = 0
        self.max = len(filenames) - 1

    @property
    def template(self):
        """numpy.ndarray: Array (h, w) of template image (grayscale)"""
        if self._template:
            return self._template

        if self._tmp is None:
            # is None, so use default template
            self._tmp_name = DEFAULT_TEMPLATE
            tmp = GrayscaleTemplateImage(DEFAULT_TEMPLATE)
            return tmp.image
        else:
            # not None, so branch on type
            if isinstance(self._tmp, str):
                # type is str, so read from string filename
                self._tmp_name = self._tmp
                tmp = GrayscaleTemplateImage(self._tmp)
                return tmp.image
            elif isinstance(self._tmp, GrayscaleTemplateImage):
                # type is GrayscaleTemplateImage, so return image part of object
                self._tmp_name = self._tmp.img_name
                return self._tmp.image

    def __iter__(self):
        return self

    def next(self):
        if self.current > self.max:
            raise StopIteration
        else:
            self.current += 1
            return FoscamImage(self.filenames[self.current - 1], tmp=self.template)


class DateRangeException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


# TODO maybe Deck gets smarter; uses different templates for each constituent images based on overall light/darkness
class Deck(object):

    def __init__(self, basedir=DEFAULT_FOLDER, date_range=None, morning=True, state=None, tmp_name=None, verbose=False):
        self._set_basedir(basedir)
        self._set_date_range(date_range)
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
                raise ValueError('"%s" does not exist as foscam image folder' % value)
        self._basedir = value

    @property
    def date_range(self):
        """pandas.DatetimeIndex: a pandas DatetimeIndex object (via pd.date_range)"""
        return self._date_range

    def _set_date_range(self, value):
        if value is None:
            # is None, so set to most recent week's range
            self._date_range = pd.date_range(DAYONE, periods=7, normalize=True)
        elif isinstance(value, list) and len(value) == 2:
            # a list of 2 objects, we will try to shoehorn into a pandas date_range
            try:
                self._date_range = pd.date_range(value[0], value[1])
            except Exception as exc:
                raise DateRangeException(str(exc))
        elif isinstance(value, pd.DatetimeIndex):
            # ftw, we have pandas date_range
            self._date_range = value
        else:
            # not None, not pd.DatetimeIndex and not len=2 list that nicely converted
            raise TypeError('see docstrings for date_range input')

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
        if value is None:
            value = DEFAULT_TEMPLATE
        else:
            if not os.path.exists(value):
                raise TypeError('Deck.tmp_name template file "%s" does not exist' % value)
        self._tmp_name = value

    def _get_filenames(self):
        """get list of filenames"""
        start = self.date_range[0].to_pydatetime().date()
        stop = self.date_range[-1].to_pydatetime().date()
        _filenames = get_date_range_foscam_files(start, stop, morning=self.morning)
        if self.state:           
            [_filenames.remove(f) for f in _filenames if self.state not in f]
        _filenames.sort(key=os.path.basename)
        return _filenames

    @property
    def images(self):
        """Get foscam image iterator."""
        if self._images:
            return self._images

        # establish template image for the entire deck to use
        if self.tmp_name:
            tmp = GrayscaleTemplateImage(self.tmp_name)
        else:
            tmp = GrayscaleTemplateImage(DEFAULT_TEMPLATE)

        # return iterator object
        fnames = self._get_filenames()
        return FoscamImageIterator(fnames, tmp=tmp)
    
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
            print fci
            # med = np.median(fci.roi_luminance)
            # if med < 191.0:
            #     guess = 'open'
            # else:
            #     guess = 'close'
            # if not fci.foscam_file.state == guess:
            #     print 'open -a Firefox file://%s # OOPS!' % fci.img_name
            # else:
            #     print med, fci.img_name


if __name__ == '__main__':

    dr = ['2017-11-11', '2017-11-15']
    state = None
    morning = False
    deck = Deck(date_range=dr, state=state, morning=morning)
    print deck.tmp_name

    #deck.overlay_roi_histograms()
    deck.show_roi_luminance_medians()

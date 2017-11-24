#!/usr/bin/env python

"""A template for use with a webcam as a sensor to control a garage door.

This module provides a template class to help determine whether the garage door is open.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

"""

import os
import cv2
from flimsy_constants import DEFAULT_TEMPLATE


class GrayscaleTemplateImage(object):

    """A template image object.

    Attributes are documented inline with the attribute's declaration (see __init__ method below).

    Properties created with the @property decorator are documented in the property's getter method.

    """

    def __init__(self, img_name=DEFAULT_TEMPLATE):
        self._img_name = None
        self._image = None
        self._set_img_name(img_name)
        self.exc_info = None

    def __str__(self):
        h, w = self.image.shape
        s = '%s has shape: (h,w) = (%d, %d)' % (self.img_name, h, w)
        return s

    @property
    def image(self):
        """numpy.ndarray: Array (h, w) of input image of interest (grayscale)."""
        if self._image:
            return self._image

        img = cv2.imread(self.img_name, 0)
        if img is None:
            raise IOError('cv2.imread returned None')

        return img

    @property
    def img_name(self):
        """string: full filename for template image; use None to get from constants"""
        return self._img_name

    def _set_img_name(self, value):
        if value:
            # not None
            if not os.path.exists(value):
                raise TypeError('template file "%s" does not exist' % value)
        else:
            # is None
            value = DEFAULT_TEMPLATE
        self._img_name = value


if __name__ == '__main__':

    tmp = GrayscaleTemplateImage()
    print tmp

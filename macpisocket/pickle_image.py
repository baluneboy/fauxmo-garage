#!/usr/bin/env python

import cPickle as pickle  # cPickle is considerably more efficient than pickle
from PIL import Image, ImageGrab


def pickle_image(img):
    """Turns an image into a data stream; required on machine sending image."""
    image = dict(data=img.tobytes(), size=img.size, mode=img.mode)
    # HIGHEST_PROTOCOL uses a more effcient representation of the object
    pickled_image = pickle.dumps(image, pickle.HIGHEST_PROTOCOL)
    return pickled_image


def unpickle_image(pickled_img):
    """Turns a data stream into an image."""
    data = pickle.loads(pickled_img)
    unpickled_image = Image.frombytes(**data)
    return unpickled_image


def demo():
    some_image = ImageGrab.grab()
    img_pickled = pickle_image(some_image)
    img_unpickled = unpickle_image(img_pickled)
    img_unpickled.show()
    

if __name__ == '__main__':
    demo()

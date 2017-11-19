#!/usr/bin/env python

import numpy as np
import cv2
from matplotlib import pyplot as plt

MIN_MATCH_COUNT = 10

img1 = cv2.imread('/home/pi/dev/programs/python/fauxmo_garage/data/box.png',0)  # queryImage
img2 = cv2.imread('/home/pi/dev/programs/python/fauxmo_garage/data/box_in_scene.png',0)  # trainImage

# Initiate ORB detector
orb = cv2.ORB_create()

# find the keypoints and descriptors with ORB
kp1, des1 = orb.detectAndCompute(img1,None)
kp2, des2 = orb.detectAndCompute(img2,None)

# Next we create a BFMatcher object with distance measurement cv2.NORM_HAMMING
# (since we are using ORB) and crossCheck is switched on for better results.
# Then we use Matcher.match() method to get the best matches in two images. We
# sort them in ascending order of their distances so that best matches (with low
# distance) come to front. Then we draw only first 10 matches (Just for sake of
# visibility. You can increase it as you like)

# create BFMatcher object
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Match descriptors.
matches = bf.match(des1,des2)

# Sort them in the order of their distance.
matches = sorted(matches, key = lambda x:x.distance)

# Draw first 10 matches.
img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:10],None,flags=2)

plt.imshow(img3),plt.show()


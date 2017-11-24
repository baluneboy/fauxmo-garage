#!/usr/bin/env python

"""This module utilizes argparse from the standard library to define what arguments it requires, and figure out how to
parse those from sys.argv.  The argparse module automatically generates help and usage messages and issues errors when
users give the program invalid arguments.
"""

# TODO mutually exclusive inputs "g" for gather stats (histogram/update?) vs. "s" show image in Firefox
# TODO if level=3 for verbosity (-vvv), then show marked up image and detailed analysis results
# TODO for "g" option to "gather", we build local html file showing markup in all images matching pattern (cache dir markup)

import os
import re
import argparse
import datetime
from dateutil import parser as date_parser

from flimsy_constants import DEFAULT_FOLDER, DEFAULT_TEMPLATE

# TODO replace DateRange with pandas date_range?
from pims.utils.datetime_ranger import DateRange

_EXPECT_AGES = ['YOUNGEST', 'OLDEST']
_DEFAULT_DATE = datetime.datetime.now().date() - datetime.timedelta(days=1)
_DEFAULT_AGE = 'youngest'
#DEFAULT_FOLDER = '/Users/ken/Pictures/foscam'
_DEFAULT_PATTERN = '\d{4}-\d{2}-\d{2}_\d{2}_\d{2}_(open|close)\.jpg' # LIKE 2017-11-09_06_07_close.jpg
#DEFAULT_TEMPLATE = '/Users/ken/Pictures/foscam/template.jpg'
#_DEFAULT_MAXDIST = 2    # maximum distance to start pixel for flood fill
#_DEFAULT_THRESH = 100   # threshold for flood fill; less than threshold is open
_DEFAULT_BLURSIZE = 5   # size of kernel for Gaussian blur (must be positive and odd)
_DEFAULT_CLIPLIM = 3.0  # clip limit for CLAHE
_DEFAULT_GRIDSIZE = 8   # tile grid size for CLAHE


def date_str(d):
    """return datetime date object converted from input string, d"""
    dtm = date_parser.parse(d)
    return dtm.date()


def age_str(t):
    """return uppercase of input string, provided it exists among expected"""
    t = t.upper()
    if t not in _EXPECT_AGES:
        raise argparse.ArgumentTypeError('"%s" is not in [%s]' % (t, ','.join(_EXPECT_AGES)))
    return t


def folder_str(f):
    """return string provided only if this folder exists"""
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError('"%s" does not exist as foscam image folder' % f)
    return f


def pattern_str(p):
    """return string provided only if it is a valid regular expression pattern string"""
    try:
        re.compile(p)
        is_valid = True
    except re.error:
        is_valid = False
    if not is_valid:
        raise argparse.ArgumentError('"%s" does not appear to be a valid regular expression')
    return p


def template_str(t):
    """return string provided only if template image exists"""
    if not os.path.exists(t):
        raise argparse.ArgumentTypeError('"%s" does not exist as template image' % t)
    return t


#def maxdist_str(r):
#    """return int, d, converted from string, s; use as max dist (d, d, d) to start pixel for flood fill"""
#    try:
#        d = int(r)
#    except Exception, e:
#        raise argparse.ArgumentTypeError('int max dist to start pixel (flood fill) could not be converted from %s' % e.message)
#
#    if d < 1 or d > 5:
#        raise argparse.ArgumentTypeError('int max dist to start pixel (flood fill) has to be 1 <= d <= 5')
#
#    return d


#def thresh_str(r):
#    """return int, d, converted from string, s; use as upper limit on flood fill pixel count when door is open"""
#    try:
#        d = int(r)
#    except Exception, e:
#        raise argparse.ArgumentTypeError('int upper lim on flood fill pixel count (door open) could not be converted from %s' % e.message)
#
#    if d < 1:
#        raise argparse.ArgumentTypeError('int upper lim on flood fill pixel count (door open) must be greater than 1')
#
#    return d


def blursize_str(r):
    """return int, b, converted from string, r; use as size of kernel for Gaussian blur"""
    try:
        b = int(r)
    except Exception, e:
        raise argparse.ArgumentTypeError('int kernel size for Gaussian blur could not be converted from %s' % e.message)

    # verify integer is positive for blur kernel size
    if b < 1:
        raise argparse.ArgumentTypeError('int kernel size for Gaussian blur must be positive')

    # verify integer is odd
    if b % 2 == 0:
        raise argparse.ArgumentTypeError('int kernel size for Gaussian blur must be odd')
    
    return b


def cliplim_str(r):
    """return float, c, converted from string, r; use as clipLimit for CLAHE histogram equalization"""
    try:
        c = float(r)
    except Exception, e:
        raise argparse.ArgumentTypeError('float clipLimit for CLAHE could not be converted from %s' % e.message)

    # verify float is positive, non-zero for cliplim
    if c <= 0:
        raise argparse.ArgumentTypeError('float cliplim for CLAHE must be positive')
    
    return c


def gridsize_str(r):
    """return int, b, converted from string, r; use as tileGridSize for CLAHE histogram equalization"""
    try:
        b = int(r)
    except Exception, e:
        raise argparse.ArgumentTypeError('int gridsize for CLAHE could not be converted from %s' % e.message)

    # verify integer is at least 2 for gridsize
    if b < 2:
        raise argparse.ArgumentTypeError('int gridsize for CLAHE must be >= 2')
    
    return b


def show_args(args):
    """print arguments"""

    # demo show
    my_date = args.date
    if args.verbosity == 2:
        print "date of interest is {}".format(str(args.date))
    elif args.verbosity == 1:
        print "date = {}".format(str(args.date))
    else:
        print my_date
    print args


def parse_inputs():
    """parse input arguments using argparse from standard library"""
    parser = argparse.ArgumentParser(description='"Open the pod bay doors..."')

    # date of interest
    help_date = "date of interest; today's default is %s" % str(_DEFAULT_DATE)
    parser.add_argument('-d', '--date', default=_DEFAULT_DATE,
                        type=date_str,
                        help=help_date)

    # age of image for a given date
    help_age = 'age of image; default=%s' % _DEFAULT_AGE
    parser.add_argument('-a', '--age', default=_DEFAULT_AGE,
                        choices=[age.lower() for age in _EXPECT_AGES],
                        type=age_str,
                        help=help_age)

    # foscam image directory
    help_folder = 'foscam image directory; default=%s' % DEFAULT_FOLDER
    parser.add_argument('-f', '--folder', default=DEFAULT_FOLDER,
                        type=folder_str,
                        help=help_folder)

    # regular expression for foscam image file
    help_pattern = 'foscam image file; default=%s' % _DEFAULT_PATTERN
    parser.add_argument('-p', '--pattern', default=_DEFAULT_PATTERN,
                        type=pattern_str,
                        help=help_pattern)

    # template image file
    help_template = 'template image; default=%s' % DEFAULT_TEMPLATE
    parser.add_argument('-t', '--template', default=DEFAULT_TEMPLATE,
                        type=template_str,
                        help=help_template)

    ## int max dist to start pixel for flood fill converted from string
    #help_maxdist = "max dist to start pixel for flood fill; default=%d" % _DEFAULT_MAXDIST
    #parser.add_argument('-r', '--maxdist', default=_DEFAULT_MAXDIST,
    #                    type=maxdist_str,
    #                    help=help_maxdist)

    ## int upper lim on flood fill pixel count (when door open) converted from string
    #help_thresh = "max dist to start pixel for flood fill; default=%d" % _DEFAULT_THRESH
    #parser.add_argument('-e', '--thresh', default=_DEFAULT_THRESH,
    #                    type=thresh_str,
    #                    help=help_thresh)
    
    # int size of kernel for Gaussian blur (must be positive and odd)
    help_blursize = "size of kernel for Gaussian blur; default=%d" % _DEFAULT_BLURSIZE
    parser.add_argument('-b', '--blursize', default=_DEFAULT_BLURSIZE,
                        type=blursize_str,
                        help=help_blursize)    
    
    # float clip limit for CLAHE
    help_cliplim = "clip limit for CLAHE; default=%.1f" % _DEFAULT_CLIPLIM
    parser.add_argument('-c', '--cliplim', default=_DEFAULT_CLIPLIM,
                        type=cliplim_str,
                        help=help_cliplim)
    
    # int tile grid size for CLAHE
    help_gridsize = "tile grid size for CLAHE; default=%d" % _DEFAULT_GRIDSIZE
    parser.add_argument('-r', '--gridsize', default=_DEFAULT_GRIDSIZE,
                        type=gridsize_str,
                        help=help_gridsize)
    
    # mutually exclusive options (-g for gather, -s for show)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-g', '--gatherstats', action='store_true')
    group.add_argument('-y', '--showyoungest', action='store_true')
    
    # verbosity
    parser.add_argument("-v", action="count", dest='verbosity',
                        help="increase output verbosity (max of 3)")

    # get parsed args
    args = parser.parse_args()

    return args

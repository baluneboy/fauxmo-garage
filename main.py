#!/usr/bin/env python

"""Use a webcam as a sensor to control a garage door.

This module provides classes to try determine whether the garage door is open.

Example:
    Demonstrate a quick show of results::

        $ python main.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

"""

import os
import re
import disp
import output
import argparser

from pims.files.utils import get_pathpattern_files


def show_results(args, vprint):
    """use args to show results and return True"""

    # get list of files from foscam image folder
    files = get_pathpattern_files(args.folder, args.pattern)
    vprint('found %d foscam image files' % len(files), 'in %s' % args.folder, 'like "%s"' % args.pattern)
    
    # branch based on input arg for age
    if args.age == 'YOUNGEST':
        img_fname = os.path.join(args.folder, files[-1])
    else:
        img_fname = os.path.join(args.folder, files[0])
    vprint('got an image file', '%s' % img_fname, 'for analysis')

    # if option selected, then show youngest with markup before vs. after analysis
    if args.showyoungest:
        vprint('show youngest', 'analysis details', 'before vs. after ftw')    
        disp.show_before_after(img_fname, args, vprint)
        
    print args
    
    return True


def args_ok(args, print_fcn):
    """return boolean True if args ok; otherwise squawk and return False"""
    # FIXME WHEN & WHERE is pythonic spot for checking parsed args
    bln = True
    # FIXME placeholder for now
    if args.gatherstats:
        print_fcn('you chose to gather stats', 'but we are not', 'doing that yet')
        bln = False
    return bln


def get_most_recent_pic():
    #/home/pi/Pictures/foscam/2017-11-20_06_25_close.jpg
    top_dir = '/home/pi/Pictures/foscam'
    r = re.compile(r'\d{4}-\d{2}-\d{2}_\d{2}_\d{2}_(open|close)\.jpg$')
    latest_file = max(filter(r.search, os.listdir(top_dir)))
    return os.path.join(top_dir, latest_file)


def main():
    """handle input arguments and return Linux-like status code that comes from call to show game day results"""

    # parse command line arguments
    args = argparser.parse_inputs()

    # get print function based on verbosity level
    print_fun = output.get_print_fun(args.verbosity)
    print_fun('got args', 'via argparser', 'ready to check/use those and run')

    # print_fun has saturates at 3 levels of verbosity (args after 3rd make show with -vvv)

    # if args not ok, then squawk and return exit code of -1
    if not args_ok(args, print_fun):
        print_fun('args not okay', 'so do nothing', 'but return bad exit code')
        return -1
    else:
        print_fun('args okay', 'so proceed', 'and use args to show results')

    # show results
    results_ok = show_results(args, print_fun)

    if results_ok:
        # return exit code zero for success
        print_fun('done', 'with all processing', 'so return exit code of zero for success')
        return 0
    else:
        print_fun('oops', 'results NOT OK', 'return with exit code -2')
        return -2


if __name__ == '__main__':
    """run main with command line args and return exit code"""
    #sys.exit(main())
    
    import numpy as np
    from fcimage import FoscamImage
    from flimsy_constants import MEDIAN_THRESHOLD
    
    fname = get_most_recent_pic()
    fci = FoscamImage(fname)
    med = np.median(fci.roi_luminance)
    if med < MEDIAN_THRESHOLD:
        guess = 'open'
    else:
        guess = 'close'
    if not fci.foscam_file.state == guess:
        print 'open -a Firefox file://%s # OOPS!' % fci.img_name
    else:
        print 'yay', med, fci.img_name    

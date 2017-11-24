#!/usr/bin/env python

import os
import unittest
import glob
import numpy as np
from fauxmo_garage.foscam import FoscamImage


class LabelTestCase(unittest.TestCase):
    
    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        """ just do this once [whereas setUp gets called for each test]
        """
        super(LabelTestCase, cls).setUpClass()
        cwd = os.path.dirname(os.path.abspath(__file__))
        cls.topdir = cwd.replace(os.path.basename(cwd), 'data')
        # list of basenames that we are declaring as mis-labeled files
        _bads = ['2000-01-02_03_04_open.jpg',
                 ]
        cls.bad_files = [os.path.join(cls.topdir, f) for f in _bads]
        cls.all_files = glob.glob(cls.topdir + '/*jpg')
        #print len(cls.files)  # 42

    def tearDown(self):
        pass

    def test_mislabel(self):
        _bads_detected = []
        for f in self.bad_files:
            fci = FoscamImage(f)
            med = np.median(fci.roi_luminance)
            if med < 191.0:
                guess = 'open'
            else:
                guess = 'close'
            if not fci.foscam_file.state == guess:
                _bads_detected.append(f)

        len_got = len(_bads_detected)
        len_exp = len(self.bad_files)
        self.assertEqual(len_got, len_exp,
            'mis-labeled file list length (%d) does not equal expected length (%d)' % (len_got, len_exp))


if __name__ == '__main__':
    unittest.main(verbosity=2)

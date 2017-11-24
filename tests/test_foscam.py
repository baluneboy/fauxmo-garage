#!/usr/bin/env python

import os
import unittest
import glob
import numpy as np
from fauxmo_garage.foscam import FoscamFile, FoscamImage, parse_foscam_fullfilestr
from fauxmo_garage.flimsy_constants import _BASENAME_PATTERN


class FoscamFileTestCase(unittest.TestCase):
    
    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        """ just do this once [whereas setUp gets called for each test]
        """
        super(FoscamFileTestCase, cls).setUpClass()
        cwd = os.path.dirname(os.path.abspath(__file__))
        cls.topdir = cwd.replace(os.path.basename(cwd), 'data')
        cls.data_files = {}
        cls.data_files['open'] = glob.glob(cls.topdir + '/2*_open.jpg')
        cls.data_files['close'] = glob.glob(cls.topdir + '/2*_close.jpg')
        cls.data_files['cool'] = glob.glob(cls.topdir + '/1999-12-31*_open.jpg')
        cls.data_files['datetime_error'] = glob.glob(cls.topdir + '/1999-12-32*_close.jpg')

    def tearDown(self):
        pass

    #@unittest.skip("...HEY...this is a simple demonstration of skipping")
    #def test_demo_skip(self):
    #    pass

    def test_parse_foscam_fullfilestr(self):
        # work on 2 key lists
        for state in ['open', 'close']:
            for fullfilestr in self.data_files[state]:
                dtm, st = parse_foscam_fullfilestr(fullfilestr, bname_pattern=_BASENAME_PATTERN)
                self.assertEqual(st, state,
                    'parsed state (%s) does not match %s' % (st, state))
        
        # non-standard state (not open and not close)
        pat = r'^(?P<day>\d{4}-\d{2}-\d{2})_(?P<hour>\d{2})_(?P<minute>\d{2})_(?P<state>noon)\.jpg$'
        dtm, state = parse_foscam_fullfilestr('/my/path/2017-11-08_06_00_noon.jpg', bname_pattern=pat)
        self.assertEqual('noon', state,
            'parsed state (%s) does not match noon' % state)
        
        # check dtm parsing here
        fullfilestr = '/my/path/1945-67-89_12_00_open.jpg'
        with self.assertRaises(ValueError):
            dtm, st = parse_foscam_fullfilestr(fullfilestr, bname_pattern=_BASENAME_PATTERN)
        
    def test_foscam_file_datetime(self):
        for issue in ['datetime_error', ]:
            files = self.data_files[issue]
            for f in files:
                with self.assertRaises(ValueError):
                    fcf = FoscamFile(f)

    def test_foscam_file_state(self):
        for state in ['open', 'close']:
            files = self.data_files[state]
            for f in files:
                fcf = FoscamFile(f)
                self.assertEqual(state, fcf.state,
                    'parsed state (%s) does not match %s' % (fcf.state, state))


if __name__ == '__main__':
    unittest.main(verbosity=2)

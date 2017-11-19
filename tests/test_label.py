#!/usr/bin/env python

import os
import unittest
import glob


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

    def test_bad_labels(self):
        len_got = len(self.bad_files)
        len_exp = len(self.all_files)
        self.assertEqual(len_got, len_exp,
            'mis-labeled file list length (%d) does not equal expected length (%d)' % (len_got, len_exp))


if __name__ == '__main__':
    unittest.main(verbosity=2)

#!/usr/bin/env python

import os
import unittest
import glob
from fauxmo_garage.deck import FoscamImageIterator


class DeckTestCase(unittest.TestCase):

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        """ just do this once [whereas setUp gets called for each test]
        """
        super(DeckTestCase, cls).setUpClass()
        cwd = os.path.dirname(os.path.abspath(__file__))
        cls.basedir = cwd.replace(os.path.basename(cwd), 'data')
        # d1 = datetime.datetime(2017, 11, 20).date()
        # d2 = datetime.datetime(2017, 11, 21).date()
        # cls.daterange = DateRange(d1, d2)
        # cls.state = None
        # cls.morning = False
        # cls.deck = Deck(basedir=cls.basedir, daterange=cls.daterange, state=cls.state, morning=cls.morning)
        cls.files = glob.glob(cls.basedir + '/2017*jpg')

    def tearDown(self):
        pass

    def test_imageiterator(self):
        count = len(list(FoscamImageIterator(self.files)))
        exp_count = len(glob.glob(self.basedir + '/2017*jpg'))
        self.assertEqual(count, exp_count,
            'file count (%d) does not equal expected count (%d)' % (count, exp_count))


if __name__ == '__main__':
    unittest.main(verbosity=2)

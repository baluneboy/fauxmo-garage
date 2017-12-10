#!/usr/bin/env python

import os
import unittest
import datetime
import glob

from pims.files.filter_pipeline import FileFilterPipeline
from fauxmo_garage.fcimage import DateRangeStateFoscamFile


class FileFilterTestCase(unittest.TestCase):
    
    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        """ just do this once [whereas setUp gets called for each test]
        """
        super(FileFilterTestCase, cls).setUpClass()
        cwd = os.path.dirname(os.path.abspath(__file__))
        cls.topdir = cwd.replace(os.path.basename(cwd), 'data')
        cls.start = datetime.datetime(2017, 11, 10).date()
        cls.stop =  datetime.datetime(2017, 11, 17).date()
        #cls.files = [os.path.join(cls.topdir, f) for f in os.listdir(cls.topdir) if os.path.isfile(os.path.join(cls.topdir, f))]
        cls.files = glob.glob(cls.topdir + '/2*jpg')
        #print len(cls.files)  # 42

    def tearDown(self):
        pass

    def test_filter_daterange(self):
        # initialize processing pipeline (prime the pipe with callables)
        # NOTE: (morning=False, state=None) should give all files in date range
        ffp = FileFilterPipeline(
            DateRangeStateFoscamFile(self.start, self.stop, morning=False, state=None),
            #YoungFile(max_age_minutes=max_age_minutes),
            )
        filt_files = [ f for f in ffp(self.files) ]
        len_got = len(filt_files)
        len_exp = len(glob.glob(self.topdir + '/2017*jpg'))
        self.assertEqual(len_got, len_exp,
            'file list length (%d) does not equal expected filtered file list length (%d)' % (len_got, len_exp))

    def test_filter_daterange_morning(self):
        # initialize processing pipeline (prime the pipe with callables)
        ffp = FileFilterPipeline(                         #         TRUE        NONE
            DateRangeStateFoscamFile(self.start, self.stop, morning=True, state=None),
            #YoungFile(max_age_minutes=max_age_minutes),
            )
        filt_files = [ f for f in ffp(self.files) ]
        len_got = len(filt_files)
        len_exp = 28  # FIXME find better way to count up "before noon" files in data directory
        self.assertEqual(len_got, len_exp,
                'got %d "morning" files, but that does not equal expected count of %d' % (len_got, len_exp))

    def test_filter_daterange_state(self):
        for state in ['open', 'close']:
            # initialize processing pipeline (prime the pipe with callables)
            ffp = FileFilterPipeline(                         #         FALSE        STATE
                DateRangeStateFoscamFile(self.start, self.stop, morning=False, state=state),
                #YoungFile(max_age_minutes=max_age_minutes),
                )
            filt_files = [ f for f in ffp(self.files) ]
            len_got = len(filt_files)
            len_exp = 21  # FIXME find better way to count up EACH STATE files in data directory
            self.assertEqual(len_got, len_exp,
                'got %d %s files, but that does not equal expected count of %d' % (len_got, state, len_exp))


if __name__ == '__main__':
    unittest.main(verbosity=2)

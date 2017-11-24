#!/usr/bin/env python

import os
import glob
import datetime
import unittest

from fauxmo_garage.foscam import FoscamFile, FoscamImage
from fauxmo_garage.foscam import parse_foscam_fullfilestr, get_date_range_foscam_files
from fauxmo_garage.flimsy_constants import BASENAME_PATTERN, DEFAULT_TEMPLATE
from fauxmo_garage.template import GrayscaleTemplateImage


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
        cls.data_files = dict()
        cls.data_files['open'] = glob.glob(cls.topdir + '/2017*_open.jpg')
        cls.data_files['close'] = glob.glob(cls.topdir + '/2017*_close.jpg')
        cls.data_files['cool'] = glob.glob(cls.topdir + '/1999-12-31*_open.jpg')
        cls.data_files['datetime_error'] = glob.glob(cls.topdir + '/1999-12-32*_close.jpg')
        cls.fci = FoscamImage(cls.data_files['open'][0])

    def tearDown(self):
        pass

    def test_parse_foscam_fullfilestr(self):
        # work on 2 key lists
        for state in ['open', 'close']:
            for fullfilestr in self.data_files[state]:
                dtm, st = parse_foscam_fullfilestr(fullfilestr, bname_pattern=BASENAME_PATTERN)
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
            dtm, st = parse_foscam_fullfilestr(fullfilestr, bname_pattern=BASENAME_PATTERN)

    # @unittest.skip("NEED TO IRON OUT DATETIME vs. DATE ISSUE")
    def test_get_date_range_foscam_files(self):
        start = datetime.datetime(2017, 11, 14).date()
        stop = datetime.datetime(2017, 11, 18).date()
        files = get_date_range_foscam_files(start, stop, morning=False, state=None, topdir=self.topdir)
        files.sort(key=os.path.basename)
        tup1 = parse_foscam_fullfilestr(files[0])
        tup2 = parse_foscam_fullfilestr(files[-1])
        d1 = tup1[0].date()
        d2 = tup2[0].date()
        self.assertLessEqual(start, d1,
                             'first file "%s" naming comes before desired start %s' % (files[0], start))
        self.assertGreaterEqual(stop, d2,
                                'last file "%s" naming comes after desired stop %s' % (files[-1], stop))

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

    def test_foscam_image_shape(self):
        ishape = self.fci.image.shape
        ilen = len(ishape)
        elen = 3
        self.assertEqual(elen, ilen,
                         'NOT COLOR? expected %d dims (h, w) for image and got %d dims: %s' % (
                         elen, ilen, str(ishape)))

    def _crudely_verify_grayscale_from_dims(self, img):
        ishape = img.shape
        ilen = len(ishape)
        elen = 2
        self.assertEqual(elen, ilen,
            'NOT GRAYSCALE? expected %d dims (h, w) for template image and got %d dims: %s' % (elen, ilen, str(ishape)))

    # @unittest.skip("TEST LATER...TOO SLOW FOR NOW")
    def test_foscam_image_roi_lum_shape(self):
        self._crudely_verify_grayscale_from_dims(self.fci.roi_luminance)

    def test_foscam_image_template_input_varieties(self):
        fname = self.data_files['open'][0]
        fcis = [
            FoscamImage(fname, template=None),
            FoscamImage(fname, template=DEFAULT_TEMPLATE),
            FoscamImage(fname, template=GrayscaleTemplateImage(DEFAULT_TEMPLATE)),
            FoscamImage(fname, template=GrayscaleTemplateImage(DEFAULT_TEMPLATE).image),
            ]
        for fci in fcis:
            self._crudely_verify_grayscale_from_dims(fci.template)


if __name__ == '__main__':
    unittest.main(verbosity=2)

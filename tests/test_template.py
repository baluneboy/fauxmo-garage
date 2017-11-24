#!/usr/bin/env python

import os
import unittest
from fauxmo_garage.flimsy_constants import DEFAULT_TEMPLATE
from fauxmo_garage.template import GrayscaleTemplateImage


class TemplateTestCase(unittest.TestCase):
    
    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        """ just do this once [whereas setUp gets called for each test]
        """
        super(TemplateTestCase, cls).setUpClass()
        cwd = os.path.dirname(os.path.abspath(__file__))
        cls.data_dir = cwd.replace(os.path.basename(cwd), 'data')
        cls.unreadable_file = os.path.join(cls.data_dir, 'unreadable_template.jpg')
        cls.default_name = DEFAULT_TEMPLATE
        cls.default_template = GrayscaleTemplateImage(img_name=cls.default_name)

    def tearDown(self):
        pass

    def test_name_does_not_exist(self):
        bad_name = '/This/Path/Should/Not/Exist/Junk.jpg'
        with self.assertRaises(TypeError):
            template = GrayscaleTemplateImage(img_name=bad_name)

    def test_no_name_given(self):
        template = GrayscaleTemplateImage()  # no input arg img_name, so using default name
        tshape = template.image.shape
        tlen = len(tshape)
        self.assertEqual(2, tlen,
            'NOT GRAYSCALE? expected only 2 dims (h, w) for default template image, but got %d dims %s' % (tlen, str(tshape)))

    def test_image_unreadable(self):
        with self.assertRaises(IOError):
            template = GrayscaleTemplateImage(img_name=self.unreadable_file)  # bad file content
            tshape = template.image.shape  # need this line for image read method to be invoked

    def _verify_grayscale_from_dims(self, img):
        tshape = img.shape
        tlen = len(tshape)
        elen = 2
        self.assertEqual(elen, tlen,
            'NOT GRAYSCALE? expected %d dims (h, w) for template image and got %d dims: %s' % (elen, tlen, str(tshape)))

    def test_verify_grayscale_default(self):
        self._verify_grayscale_from_dims(self.default_template.image)

    def test_using_keyword_arg(self):
        template = GrayscaleTemplateImage(img_name=DEFAULT_TEMPLATE)
        self._verify_grayscale_from_dims(template.image)

    def test_not_using_keyword_arg(self):
        template = GrayscaleTemplateImage(DEFAULT_TEMPLATE)
        self._verify_grayscale_from_dims(template.image)


if __name__ == '__main__':
    unittest.main(verbosity=2)

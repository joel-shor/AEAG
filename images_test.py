"""Test images module."""

__author__ = 'shor.joel@gmail.com (Joel Shor)'


import tempfile
import unittest
import os

import images


class TestAudio(unittest.TestCase):

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

    def test_copy_audio_from_disk(self):
        filenames_to_write_imgs = {
            'word1': tempfile.mktemp(),
            'word2': tempfile.mktemp(),
        }
        for filename in filenames_to_write_imgs.values():
            self.assertFalse(os.path.exists(filename))
        images.copy_images_from_disk(
            filenames_to_write_imgs,
            media_dir=os.path.join(self.dir_path, 'testdata'),
            filename_regexp='test_images_%s.jpg')
        for filename in filenames_to_write_imgs.values():
            self.assertTrue(os.path.exists(filename))


if __name__ == '__main__':
    unittest.main()
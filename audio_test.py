"""Test audio module."""

__author__ = 'shor.joel@gmail.com (Joel Shor)'


import unittest
import os
import tempfile

import audio


class TestAudio(unittest.TestCase):

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

    def test_copy_audio_from_disk(self):
        filenames_to_write_auds = {
            'word1': tempfile.mktemp(),
            'word2': tempfile.mktemp(),
        }
        for filename in filenames_to_write_auds.values():
            self.assertFalse(os.path.exists(filename))
        audio.copy_audio_from_disk(
            filenames_to_write_auds,
            media_dir=os.path.join(self.dir_path, 'testdata'),
            filename_regexp='test_audio_%s.mp3')
        for filename in filenames_to_write_auds.values():
            self.assertTrue(os.path.exists(filename))


if __name__ == '__main__':
    unittest.main()
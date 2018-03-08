# -*- coding: utf-8 -*-
"""Check that code that interacts with public APIs works as expected.

 APIs that are checked:
 - Images

 TODO(joelshor): Add checks for:
 - Audio
 - Translations

 """

__author__ = 'shor.joel@gmail.com (Joel Shor)'

import os
import tempfile

import audio
import images
from my_credentials import credentials


def test_get_images(credentials):
    filenames_to_write_imgs = {
        'water': tempfile.mktemp(),
    }
    assert not os.path.exists(filenames_to_write_imgs['water'])
    images.get_images(filenames_to_write_imgs, credentials)
    assert os.path.exists(filenames_to_write_imgs['water'])


def test_get_audio(credentials):
    filenames_to_write_imgs = {
        'מים': tempfile.mktemp(),
    }
    assert not os.path.exists(filenames_to_write_imgs['מים'])
    audio.get_audio(word_list, credentials)
    assert os.path.exists(filenames_to_write_imgs['מים'])


if __name__ == '__main__':
    test_get_images(credentials)
    # test_get_audio(credentials)

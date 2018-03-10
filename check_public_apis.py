# -*- coding: utf-8 -*-
"""Check that code that interacts with public APIs works as expected.

 APIs that are checked:
 - Images
 - Audio
 - Translations
 """

__author__ = 'shor.joel@gmail.com (Joel Shor)'

import os
import tempfile

import audio
import images
import translation
from credentials import credentials


def test_get_translate(credentials):
    word_list = ['water']
    expected_translations = ['מָיִם', 'מים']
    translation_list = translation.get_translations(word_list, credentials, target_language='iw')
    if len(translation_list) != len(word_list):
        raise ValueError(
            'Expected translation list to be length %i, but was %i.' % (len(word_list), len(translation_list)))
    if translation_list[0] not in expected_translations:
        raise ValueError('Expected translation to be one of `%s`, but instead was `%s`.' % (
            expected_translations, translation_list[0]))


def test_get_images(credentials):
    filenames_to_write_imgs = {
        'water': tempfile.mktemp(),
    }
    assert not os.path.exists(filenames_to_write_imgs['water'])
    images.get_images(filenames_to_write_imgs, credentials)
    if not os.path.exists(filenames_to_write_imgs['water']):
        raise ValueError('Image file for `water` wasn\'t written.')


def test_get_audio(credentials):
    filenames_to_write_imgs = {
        'מים': tempfile.mktemp(),
    }
    assert not os.path.exists(filenames_to_write_imgs['מים'])
    audio.get_audio(filenames_to_write_imgs, credentials)
    if not os.path.exists(filenames_to_write_imgs['מים']):
        raise ValueError('Audio file for `מים` wasn\'t written.')


if __name__ == '__main__':
    test_get_translate(credentials)
    test_get_images(credentials)
    test_get_audio(credentials)
    print('All tests succeeded.')

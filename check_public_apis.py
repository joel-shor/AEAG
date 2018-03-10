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
    word_list = ['water', 'אַבָּא', 'אמא']
    expected_english = ['water', 'father', 'mother']
    expected_translations = ['מָיִם', 'מים', 'אַבָּא', 'אמא']
    actual_english, actual_translations = translation.get_translations(word_list, credentials, target_language='iw')
    if len(actual_english) != len(expected_english):
        raise ValueError(
            'Expected translation list to be length %i, but was %i.' % (len(expected_english), len(actual_english)))
    if len(actual_translations) != len(expected_english):  # use expected English because translation list is longer
        raise ValueError(
            'Expected translation list to be length %i, but was %i.' % (len(expected_english),
                                                                        len(actual_translations)))
    if set(actual_english) != set(expected_english):
        raise ValueError('Expected English translations to be `%s`, but was `%s`.' % (
            set(expected_english), set(actual_english)))
    if not set(actual_translations).issubset(set(expected_translations)):
        raise ValueError('Expected translation to be a subset of `%s`, but instead was `%s`.' % (
            set(expected_translations), set(actual_translations)))


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

# -*- coding: utf-8 -*-
"""Check that code that interacts with public APIs works as expected.

 APIs that are checked:
 - Images

 TODO(joelshor): Add checks for:
 - Audio
 - Translations

 """

__author__ = 'shor.joel@gmail.com (Joel Shor)'


import images
from credentials import credentials


def test_get_images(credentials):
    word_list = ['water']
    image_files = images.get_images(word_list, credentials)
    print image_files

    if not isinstance(image_files, dict):
        raise ValueError('`get_images` output wasn\'t a dictionary.')
    if len(word_list) != len(image_files):
        raise ValueError(
            'Number of returned images wasn\'t correct. Expected %i but got %i.' % (len(word_list), len(image_files)))


def test_get_audio(credentials):
    word_list = ['מים']
    audio_files = images.get_audio(word_list, credentials)

    if not isinstance(audio_files, dict):
        raise ValueError('`get_audio` output wa\'t a dictionary.')
    if len(word_list) != len(audio_files):
        raise ValueError('Number of returned audio was\'nt correct.')


if __name__ == '__main__':
    test_get_images(credentials)
    #test_get_audio(credentials)
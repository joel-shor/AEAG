# -*- coding: utf-8 -*-
"""Test translations module."""

__author__ = 'shor.joel@gmail.com (Joel Shor)'


import unittest

import translation


class TestTranslations(unittest.TestCase):

    def test_strip_diacritics(self):
        words_with_diacritics = ['חוּלצָה', 'מִכְנָסַיִים']
        words_without_diacritics = ['חולצה', 'מכנסיים']

        self.assertListEqual(
            words_without_diacritics,
            translation.strip_diacritics(words_with_diacritics))



if __name__ == '__main__':
    unittest.main()
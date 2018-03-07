"""Tests for Forvo utils."""


import forvo_utils
import unittest
import os


class TestForvoUtils(unittest.TestCase):

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

    def test_extract_mp3link_from_xml(self):
        with open(os.path.join(self.dir_path, 'testdata', 'forvo.xml')) as f:
            xml = f.read()
        mp3_link = forvo_utils._extract_mp3link_from_xml(xml)
        self.assertEqual(
            'https://apifree.forvo.com/audio/2d2g293f3k333l1g1l3f293p2q332q3j1i2c2d3h232i3335242a2f2i382j3q311f2h311g3q3a3h3n313j2d2c3c2d1m1i1m3q2q3i3c3m2a1b373a241o342p3h2b3f2p3f3h3h3j213b3b2j1j2633261f2q2l241h2i38371t1t_2j2d2p3g2k2l1p3g2e29241p2d2d2a2d1k363m2k382h1t1t',
            mp3_link)


if __name__ == '__main__':
    unittest.main()
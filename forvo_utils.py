"""EasyAnki audio stuff.

https://github.com/dveselov/python-yandex-translate

Might have to do:

pip install yandex_speech
"""

__author__ = 'shor.joel@gmail.com (Joel Shor)'


import urllib2
import xml.etree.ElementTree as ET


def _get_forvo_url(word, api_key, language='he'):
    return 'https://apifree.forvo.com/key/%s/format/xml/action/word-pronunciations/word/%s/language/%s' % (
        api_key, word, language)


def _get_forvo_xml(word, api_key, language='he'):
    response = urllib2.urlopen(_get_forvo_url(word, api_key, language))
    xml = response.read()


def get_mp3_link(word, api_key, language='he'):
    xml_string = _get_forvo_xml(word, api_key, language=language)
    return _extract_mp3link_from_xml(xml_string)


def _extract_mp3link_from_xml(xml_string):
    tree = ET.fromstring(xml_string)
    def _get_and_check_unique(item, item_name):
        sub_items = item.findall(item_name)
        if len(sub_items) > 1:
            raise ValueError('Too many `pathmp3` items found.')
        if not sub_items:
            raise ValueError('No `pathmp3` item found.')
        return sub_items[0].text
    paths_and_ratings = []
    for item in tree:
        pathmp3 = _get_and_check_unique(item, 'pathmp3')
        rate = int(_get_and_check_unique(item, 'rate'))
        paths_and_ratings.append((rate, pathmp3))

    # Return highest rated audio.
    paths_and_ratings.sort(reverse=True)
    return paths_and_ratings[0][1]
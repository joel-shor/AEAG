"""Queries Google's Translate API for translations.

This uses Google's Client Translation API. We use this API rather than the Cloud API because not all services we want
for this project are migrated to the Clout API. More details can be found at:
https://developers.google.com/api-client-library/python/apis/translate/v2

Follow the instructions there to download the Google API Python client. It might
be as simple as running:

pip install --upgrade google-api-python-client

A canonical example for using Translate can be found at:
https://github.com/google/google-api-python-client/tree/master/samples/translate
"""


__author__ = 'shor.joel@gmail.com (Joel Shor)'

import string

from googleapiclient.discovery import build


def _is_english(word):
    # NOTE: This is a hack for sorting between English and Hebrew, which have disjoint character sets. This will have
    # to be made more general (ex perhaps with `langdetect`) for more languages.
    return set(word).issubset(set(string.printable))


def get_translations(single_words, credentials, target_language='iw', max_words=100):
    """Translate list of words from English to target language or the reverse.

    Args:
        single_words: A Python list of single words. Each word can be English or foreign.
        credentials: A object with Google Translate credentials.
        target_language: Language code of target language.
        max_words: Google translate API only translates a few words at a time, so batch them.

    Return:
        A 2-tuple of (English word list, translation word list).
    """
    # Sort words into foreign or not.
    english_words = []
    foreign_words = []
    for word in single_words:
        english_words.append(word) if _is_english(word) else foreign_words.append(word)

    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.
    service = build('translate', 'v2', developerKey=credentials.translate.developerKey)
    word_pairs = []
    for batch_i in xrange(0, len(english_words), max_words):
        cur_english_words = english_words[batch_i: batch_i + max_words]
        translations = service.translations().list(
            source='en',
            target=target_language,
            q=cur_english_words,
        ).execute()
        cur_foreign_words = [x['translatedText'].encode('utf-8') for x in translations['translations']]
        word_pairs.extend(zip(cur_english_words, cur_foreign_words))
    for batch_i in xrange(0, len(foreign_words), max_words):
        cur_foreign_words = foreign_words[batch_i: batch_i + max_words]
        decoded_foreign_words = [x.decode('utf-8') for x in cur_foreign_words]
        translations = service.translations().list(
            source=target_language,
            target='en',
            q=decoded_foreign_words,
        ).execute()
        cur_english_words = [x['translatedText'].encode('utf-8') for x in translations['translations']]
        word_pairs.extend(zip(cur_english_words, cur_foreign_words))
    english_words, translated_words = zip(*word_pairs)

    for word_list in [english_words, translated_words]:
        assert isinstance(word_list, tuple)
        assert len(word_list) == len(single_words)
        for word in word_list:
            assert isinstance(word, str)  # not unicode!!
    return english_words, translated_words


def strip_diacritics(word_list):
    """Strips words of diacritic marks.

    Args:
        word_list: A list of Hebrew words, with diacritics.

    Returns:
        A list of Hebrew words without diacritics.
    """
    def _strip_word(word):
        if isinstance(word, str):
            word = word.decode('utf-8')
        else:
            if not isinstance(word, unicode):
                raise ValueError('Word input must be string or unicode. Instead, was %s' % type(word))
        stripped_word = ''
        for cur_letter in word:
            cur_letter_unicode = ord(cur_letter)
            if cur_letter_unicode < 1425 or cur_letter_unicode > 1479:
                stripped_word += cur_letter
        return stripped_word.encode('utf-8')
    return [_strip_word(word) for word in word_list]
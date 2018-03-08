"""EasyAnki translation stuff.

TODO(joelshor): Make sure this is all accurate.

This uses Google's Client Translation API. More details can be found at:
https://developers.google.com/api-client-library/python/apis/translate/v2

Follow the instructions there to download the Google API Python client. It might
be as simple as running:

pip install --upgrade google-cloud-translate

A canonical example for using Image Search can be found at:
https://github.com/google/google-api-python-client/tree/master/samples/translate
"""


__author__ = 'shor.joel@gmail.com (Joel Shor)'

# Imports the Google Cloud client library
from googleapiclient.discovery import build


def get_translations(word_list, credentials, target_language='iw', max_words=100):
    """Translate list of words.

    Args:
        word_list: A Python list of English words.
        credentials: A object with Google Translate credentials.
        target_language: Language code of target language.
        max_words: Google translate API only translates a few words at a time, so batch them.

    Return:
        A list of translations.
    """
    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.
    service = build('translate', 'v2', developerKey=credentials.translate.developerKey)
    translated_words = []
    for batch_i in xrange(0, len(word_list), max_words):
        translations = service.translations().list(
            source='en',
            target=target_language,
            q=word_list[batch_i: batch_i + max_words],
        ).execute()
        translated_words.extend([x['translatedText'].encode('utf-8') for x in translations['translations']])
    assert isinstance(translated_words, list)
    assert len(translated_words) == len(word_list)
    for translated_word in translated_words:
        assert isinstance(translated_word, str)  # not unicode!!
    return translated_words

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
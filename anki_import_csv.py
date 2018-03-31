"""Formats file names and content for importing into Anki.

Specifically, `make_csv_rows` produces output that can be directly written to a CSV file and imported by the Anki
card import mechanism.
"""

__author__ = 'shor.joel@gmail.com (Joel Shor)'

import os

JPEG_FORMAT = '<img src="%s">'
MP3_FORMAT = '[sound:%s]'


def _img_format(full_filename):
    return JPEG_FORMAT % os.path.basename(full_filename)


def _mp3_format(full_filename):
    return MP3_FORMAT % os.path.basename(full_filename)


def _validate_inputs(translation_dict, image_dict, audio_dict, extra_info):
    """Validates inputs."""
    # Inputs should be dictionaries, and be the same size.
    assert isinstance(translation_dict, dict)
    expected_size = len(translation_dict)
    assert isinstance(image_dict, dict)
    if len(image_dict) != expected_size:
        raise ValueError('Image dictionary was expected to be size %i, but '
                         'instead was size %i' % (expected_size, len(image_dict)))
    assert isinstance(audio_dict, dict)
    if len(audio_dict) != expected_size:
        raise ValueError('Audio dictionary was expected to be size %i, but '
                         'instead was size %i' % (expected_size, len(audio_dict)))
    if extra_info:
        assert isinstance(extra_info, dict)
        if len(extra_info) != expected_size:
            raise ValueError('Extra info dictionary was expected to be size %i, but '
                             'instead was size %i' % (expected_size, len(extra_info)))

    # English lists and translation lists should be the same.
    if set(translation_dict.keys()) != set(image_dict.keys()):
        raise ValueError('English words in translation dictionary and image dictionary need to be the same.')
    if extra_info:
        if not set(extra_info.keys()).issubset(translation_dict.keys()):
            raise ValueError('English words in extra info must be a subset of English words in translation dictionary.')
    if set(translation_dict.values()) != set(audio_dict.keys()):
        raise ValueError('Translations in translation dictionary and audio dictionary need to be the same.')


def make_csv_format(translation_dict, image_dict, audio_dict, extra_info=None):
    """Formats file locations for importing into Anki.

    Args:
        translation_dict: A dict of {English: translation}.
        image_dict: A dict of {English: image filename}.
        audio_dict: A dict of {translation: audio filename}.
        extra_info: An optional dict of {English: list of extra info}.

    Returns:
        A tuple of rows to be written to a CSV file on disk. The file format is
        expected to be Anki-import compatible. The rows represent Anki notes. The
        output should be able to be passed to `csv.Writer.writerows()`. Order is
        `(English word, translation, image, audio, extra info...)`
    """
    _validate_inputs(translation_dict, image_dict, audio_dict, extra_info)

    # Construct rows.
    if extra_info:
        return ((_img_format(image_dict[eng]), trans, _mp3_format(audio_dict[trans]), eng) +
                tuple(extra_info.get(eng, []))
                for eng, trans in translation_dict.items())
    else:
        return ((_img_format(image_dict[eng]), trans, _mp3_format(audio_dict[trans]), eng)
                for eng, trans in translation_dict.items())


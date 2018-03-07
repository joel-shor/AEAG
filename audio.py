"""EasyAnki audio stuff.

https://github.com/dveselov/python-yandex-translate

Might have to do:

pip install yandex_speech
"""

__author__ = 'shor.joel@gmail.com (Joel Shor)'


import os
import shutil
import urllib

#from yandex_translate import YandexTranslate
import forvo_utils


# Possibly also use Forvo: https://github.com/nosamanuel/pyforvo

def get_audio(filenames_to_write_imgs, credentials, method='Forvo'):
    """Fetch audio from the web.

    Args:
        filenames_to_write_imgs: A dictionary of {translated word: full filename to copy audio to}.
        method: A string describing how to fetch audio. It's basically a switch
            between entirely different codepaths.
    """
    return {
        'Forvo': get_audio_from_forvo,
        'Yandex': get_audio_from_yandex,
    }(filenames_to_write_imgs, credentials)


def get_audio_from_forvo(filenames_to_write_imgs, credentials):
    """Fetch audio from Forvo online word dictionary."""
    for word, destination_fn in filenames_to_write_imgs.items():
        mp3_link = forvo_utils.get_mp3_link(word, credentials.audio.forvoAPIKey)
        urllib.urlretrieve(mp3_link, destination_fn)


def get_audio_from_yandex(filenames_to_write_imgs, credentials):
    """Fetch audio from Yandex translate.

    Examples from: https://github.com/dveselov/python-yandex-translate

    Get keys from https://translate.yandex.com/developers/keys."""
    raise ValueError('Yandex translate not supported.')


def copy_audio_from_disk(filenames_to_write_auds, media_dir, filename_regexp="pronunciation_he_%s.mp3"):
    """Copies audio from one directory to another.

    Args:
        filenames_to_write_imgs: A dictionary of {English word: full filename to copy audio to}.
        media_dir: The location on disk we expect to find the files.
        filename_regexp: The expected filename, with one spot for the word.

    Raises:
        ValueError: If any audio file doesn't exist.
    """
    for word, target_location in filenames_to_write_auds.items():
        existing_filename = os.path.join(media_dir, filename_regexp % word)
        if not os.path.exists(existing_filename):
            raise ValueError("Word %s was expecting audio file %s, but it didn't "
                             "exist." % (word, existing_filename))
        shutil.copyfile(existing_filename, target_location)
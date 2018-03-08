"""EasyAnki audio stuff.

https://github.com/dveselov/python-yandex-translate

Might have to do:

pip install yandex_speech
"""

__author__ = 'shor.joel@gmail.com (Joel Shor)'


import logging
import os
import shutil
import urllib

import forvo_utils


# Possibly also use Forvo: https://github.com/nosamanuel/pyforvo

def get_audio(filenames_to_write_imgs, credentials, method='Forvo'):
    """Fetch audio from the web.

    Args:
        filenames_to_write_imgs: A dictionary of {translated word: full filename to copy audio to}.
        method: A string describing how to fetch audio. It's basically a switch
            between entirely different codepathes.

    Returns:
        A list of words for which audio fetching didn't work.
    """
    return {
        'Forvo': get_audio_from_forvo,
    }[method](filenames_to_write_imgs, credentials)


def get_audio_from_forvo(filenames_to_write_imgs, credentials):
    """Fetch audio from Forvo online word dictionary."""
    words_without_audio = []
    for word, destination_fn in filenames_to_write_imgs.items():
        mp3_link = forvo_utils.get_mp3_link(word, credentials.audio.forvoAPIKey)
        if mp3_link:
            urllib.urlretrieve(mp3_link, destination_fn)
        else:
            logging.warning('Couldn\'t find audio on Forvo for `%s`.' % word)
            words_without_audio.append(word)
    return words_without_audio


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
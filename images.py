"""EasyAnki images stuff.

This uses Google's `Custom Search API`. More details can be found at:
https://developers.google.com/custom-search/

The Python Client library info can be found at:
https://developers.google.com/api-client-library/python/apis/customsearch/v1

Follow the instructions there to download the Google API Python client. It might
be as simple as running:

pip install --upgrade google-api-python-client

A canonical example for using Image Search can be found at:
https://github.com/google/google-api-python-client/blob/master/samples/customsearch/main.py
"""


__author__ = 'shor.joel@gmail.com (Joel Shor)'


import logging
import os
import shutil
import urllib
from multiprocessing import Pool

from googleapiclient.discovery import build


def get_images(filenames_to_write_imgs, credentials, max_processes=100):
    """Fetch images from a Google Custom Search Engine.

    Based on instructions for `Custom Search` at
    https://developers.google.com/custom-search/docs/tutorial/creatingcse
    and
    https://developers.google.com/api-client-library/python/apis/customsearch/v1
    and
    https://github.com/google/google-api-python-client/tree/master/samples/customsearch.

    Args:
        filenames_to_write_imgs: A dictionary of {English word: full filename to copy image to}.
        credentials: A object with Google CSE credentials.
        max_processes: Maximum number of threads to run simultaneously.

    Returns:
        A list of words that failed.
    """
    if not isinstance(filenames_to_write_imgs, dict):
        raise ValueError('`filenames_to_write_imgs` must be a dict. Instead, was %s' % type(filenames_to_write_imgs))
    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.
    service = build("customsearch", "v1", developerKey=credentials.images.developerKey)

    # Build a pool of works to fetch many images in parallel.
    pool = Pool(processes=max_processes)

    def _fetch_single_image(word_and_destination_fn):
        """Copies a web image to a destination on the local disk.

        Args:
            word_and_destination_fn: (word, destination filename)

        Returns:
            `word` if the fetch failed, else `None`.
        """
        word, destination_fn = word_and_destination_fn
        res = service.cse().list(
            q=word,
            cx=credentials.images.cxString,
            searchType="image",
            num=1).execute()
        img_url = res['items'][0]['link']
        try:
            print('about to retrieve: ', word)
            urllib.urlretrieve(img_url, destination_fn)
            print('retrieved: ', word)
        except:
            logging.error('Failed on word/url: %s/%s' % (word, img_url))
            return word
        return None

    words_that_failed = pool.map(_fetch_single_image, filenames_to_write_imgs.items(), chunksize=1)
    words_that_failed = filter(lambda a: a != None, words_that_failed)
    return words_that_failed


def copy_images_from_disk(filenames_to_write_imgs, media_dir, filename_regexp="image_%s.jpg"):
    """Copies images from one directory to another.

    Args:
        filenames_to_write_imgs: A dictionary of {English word: full filename to copy image to}.
        media_dir: The location on disk we expect to find the files.
        filename_regexp: The expected filename, with one spot for the word.

    Raises:
        ValueError: If any image file doesn't exist.
    """
    for word, target_location in filenames_to_write_imgs.items():
        existing_filename = os.path.join(media_dir, filename_regexp % word)
        if not os.path.exists(existing_filename):
            raise ValueError("Word `%s` was expecting image file %s, but it didn't "
                             "exist." % (word, existing_filename))
        shutil.copyfile(existing_filename, target_location)
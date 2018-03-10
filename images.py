"""Queries a Google Custom Search Engine for images.

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

from googleapiclient.discovery import build


def _fetch_single_image(word, destination_fn, service, credentials):
    """Copies a web image to a destination on the local disk.

    Args:
        word: Word to find image for.
        destination_fn: Destination filename for image.
        service: The Google Client API service object.
        credentials: The credentials object.

    Returns:
        `word` if the fetch failed, else `None`.
    """
    res = service.cse().list(
        q=word,
        cx=credentials.images.cxString,
        searchType="image",
        fileType="jpg",  # this is just to match the filename template defined in `main.py`
        num=1).execute()
    img_url = res['items'][0]['link']
    try:
        logging.info('about to retrieve: %s', word)
        urllib.urlretrieve(img_url, destination_fn)
        logging.info('retrieved: %s', word)
    except Exception as e:
        logging.error('Failed on word/url: %s/%s' % (word, img_url))
        logging.info(e)
        return word
    return None


def get_images(filenames_to_write_imgs, credentials):
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

    Returns:
        A list of words that failed.
    """
    if not isinstance(filenames_to_write_imgs, dict):
        raise ValueError('`filenames_to_write_imgs` must be a dict. Instead, was %s' % type(filenames_to_write_imgs))

    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.
    service = build("customsearch", "v1", developerKey=credentials.images.developerKey)

    # TODO(joelshor): Use `multiprocessing.Pool` to fetch many images in parallel.
    words_that_failed = []
    for word, destination_fn in filenames_to_write_imgs.items():
        if _fetch_single_image(word, destination_fn, service, credentials):
            words_that_failed.append(word)

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
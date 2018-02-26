"""EasyAnki images stuff."""

import os
# Replace this with non-Tensorflow Google stuff.
import tensorflow as tf


def get_images_sync(word_list):
    """Synchronously fetches images.

    Args:
        word_list: A list of English words.

    Returns:
        A dictionary of {English word: image}.
    """
    pass


def write_images(images_dict, output_dir):
    """Writes images to disk.

    Args:
        images_dict: A dictionary of {Engish word: numpy array}.
        output_dir: The directory where all the images will be written.
    """
    FILENAME_FORMAT = "%s.jpg"
    for english_word, image in images_dict.items():
        filename = os.path.join(output_dir, FILENAME_FORMAT % english_word)
        with tf.gfile.Open(filename, "w") as f:
            # TODO(joelshor): This is wrong. Do jpeg format stuff.
            f.write(image)
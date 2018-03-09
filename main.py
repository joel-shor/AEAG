'''Main entry point for EasyAnki, the easy way to make Anki flashcards.

The program does the following:
1) Parses a table from disk containing Enlgish words, translations, and optional side info.
2) Finds a representative image from the web or from disk.
3) Finds a native speaker audio file for the word, from the web or from disk.
4) Writes everything to a target directory.
5) Writes a CSV with the card info that can be imported into an Anki deck.
'''

__author__ = 'shor.joel@gmail.com (Joel Shor)'


import argparse
import csv
import logging
import os

import audio as audio_lib
from credentials import credentials
import images as images_lib
import translation as translate_lib
import anki_import_csv


class EasyAnkiArgParser(argparse.ArgumentParser):

  def __init__(self):
    super(EasyAnkiArgParser, self).__init__()

    # Input arguments.
    self.add_argument(
        '--input_file',
        default='',
        help='The location of the input file. Must be a comma-separated CSV file. The format depends on other input '
             'arguments.')
    self.add_argument(
        '--input_includes_translations',
        action='store_true',
        help='If `False`, input CSV file is just a list of newline-separated English words. If `True`, input CSV must '
             'be in the following format: '
             '`English`,`Translation without diacritics`,`Optional translation with diacritics`.')

    # Arguments controlling media behavior.
    self.add_argument(
        '--already_downloaded_media_dir',
        default='',
        help='If non-empty, looks for appropriately named media in this folder (images and audio) instead of trying to '
             'download them.')

    # Output arguments.
    self.add_argument(
        '--output_dir',
        default='',
        help='The directory where the files will be written to disk. This will often be Anki\'s media folder.')
    self.add_argument(
        '--output_csv_file',
        default='',
        help='The location of the Anki import csv file to generate.')



NUM_INPUT_FILE_FIELDS = 3
IMAGE_FILENAME_FORMAT = '%s.jpg'  # image filename to write if fetched from web
AUDIO_FILENAME_FORMAT = '%s.mp3'  # audio filename to write if fetched from web

class WordTranslationPairs(object):
    """A thin wrapper around a list of tuples."""
    def __init__(self, tuple_list, english_index=0, translation_index=1):
        self._tuple_list = tuple_list
        self._english_index = english_index
        self._translation_index = translation_index
        self._validate_tuple_list()

    def _validate_tuple_list(self):
        """Check that tuples have the right number of elements."""
        assert self._tuple_list
        for tuple in self._tuple_list:
            if len(tuple) != NUM_INPUT_FILE_FIELDS:
                raise ValueError(
                    "Tuple %s had %i fields instead of the expected "
                    "number: %i" % (tuple, len(tuple), NUM_INPUT_FILE_FIELDS))
            assert len(tuple) == NUM_INPUT_FILE_FIELDS

    @property
    def english_words(self):
        return [x[0] for x in self._tuple_list]

    @property
    def translations(self):
        return [x[1] for x in self._tuple_list]

    @property
    def data(self):
        return self._tuple_list

    @property
    def translation_dict(self):
        return {x[self._english_index]: x[self._translation_index] for x in self.data}

    def get_translation(self, english_word):
        return self.translation_dict[english_word]

    @property
    def reverse_translation_dict(self):
        return {x[self._translation_index]: x[self._english_index] for x in self.data}

    def get_english(self, translated_word):
        return self.reverse_translation_dict[translated_word]

    @property
    def extra_info(self):
        extra_info_indices = range(NUM_INPUT_FILE_FIELDS)
        extra_info_indices.remove(self._english_index)
        extra_info_indices.remove(self._translation_index)
        if extra_info_indices:
            return {x[self._english_index]: (x[i] for i in extra_info_indices)
                    for x in self.data}
        else:
            return None

    def remove_translated_word(self, translated_word):
        index = -1
        for i in xrange(len(self._tuple_list)):
            tup = self._tuple_list[i]
            if tup[self._translation_index] == translated_word:
                index = i
                break
        if index == -1:
            raise ValueError('Tried to deleted translated word `%s`, but couldn\'t find it in the word list.' %
                             translated_word)
        del self._tuple_list[index]


def parse_word_translation_csv(input_filename, delimiter=","):
    """Parses input file and returns a `WordTranslationPairs`."""
    with open(input_filename, 'r') as f:
        lines = f.readlines()
    reader = csv.reader(lines, delimiter=delimiter, doublequote=True)
    word_translation_pairs = [row for row in reader]
    return WordTranslationPairs(word_translation_pairs)


def parse_english_only_csv(input_filename):
    with open(input_filename, 'r') as f:
        lines = f.readlines()
    reader = csv.reader(lines, doublequote=True)
    english_only = [row for row in reader]
    for word in english_only:
        if len(word) > 1:
            raise ValueError('Malformed input: %s' % word)
    return [x[0] for x in english_only]


def _files_exist(filename_list):
    for filename in filename_list:
        if not os.path.exists(filename):
            raise ValueError('`%s` should have existed, but it doesn\'t.' % filename)

def remove_existing_filenames(full_filenames, target_dir):
    """Removes arguments corresponding to media that already exists.

    Args:
        filename_dict: A dictionary of {word: filenames}.
        target_dir: The directory to check for name collisions.

    Raises:
        ValueError: If any file in `target_dir` has the same basename as any
            files in `full_filenames`.
    """
    basenames = {k: os.path.basename(v) for k, v in full_filenames.items()}
    for word, basename in basenames.items():
        if os.path.isfile(os.path.join(target_dir, basename)):
            del full_filenames[word]
            logging.info('%s already exists, so deleting %s.' % (basename, word))


def main(argv=None):
    del argv

    # Parse input CSV file. The expected format of the input file depends on commandline arguments.
    if FLAGS.input_includes_translations:
        word_translation_pairs = parse_word_translation_csv(FLAGS.input_file)
    else:
        english_words = parse_english_only_csv(FLAGS.input_file)
        translated_words = translate_lib.get_translations(english_words, credentials)
        logging.info('Translated %i words.' % len(translated_words))
        translated_words_no_diacritics = translate_lib.strip_diacritics(translated_words)
        word_translation_pairs = WordTranslationPairs(
            zip(english_words, translated_words_no_diacritics, translated_words))
    assert isinstance(word_translation_pairs, WordTranslationPairs)

    # Determine full filename where media should be written to.
    filenames_to_write_imgs = {
        word: os.path.join(FLAGS.output_dir, IMAGE_FILENAME_FORMAT % word) for word in
        word_translation_pairs.english_words}
    filenames_to_write_auds = {
        word: os.path.join(FLAGS.output_dir, AUDIO_FILENAME_FORMAT % word) for word in
        word_translation_pairs.translations}
    # Remove entries corresponding to media that already exists.
    # NOTE: This function modifies the first argument.
    remove_existing_filenames(filenames_to_write_imgs, FLAGS.output_dir)
    remove_existing_filenames(filenames_to_write_auds, FLAGS.output_dir)

    # Get images, and audio.
    # TODO(joelshor): Try to combine approaches and fetch media if it doesn't exist.
    if FLAGS.already_downloaded_media_dir:
        images_lib.copy_images_from_disk(
            filenames_to_write_imgs, FLAGS.already_downloaded_media_dir)
        audio_lib.copy_audio_from_disk(
            filenames_to_write_auds, FLAGS.already_downloaded_media_dir)
    else:
        words_without_imgs = images_lib.get_images(filenames_to_write_imgs, credentials)
        words_without_audio = audio_lib.get_audio(filenames_to_write_auds, credentials)

        # Remove words without audio from flashcard list.
        logging.error('Couldn\'t find images for: ')
        for english_word in words_without_imgs:
            translated_word = word_translation_pairs.get_translation(english_word)
            logging.error('%s / %s' % (english_word, translated_word))
        logging.error('Couldn\'t find audio for: ')
        for translated_word in words_without_audio:
            english_word = word_translation_pairs.get_english(translated_word)
            logging.error('%s / %s' % (english_word, translated_word))
        english_words_to_remove = set(words_without_imgs).union(
            set([word_translation_pairs.get_english(x) for x in words_without_audio]))
        for english_word in english_words_to_remove:
            translated_word = word_translation_pairs.get_translation(english_word)
            del filenames_to_write_auds[translated_word]
            del filenames_to_write_imgs[english_word]
            word_translation_pairs.remove_translated_word(translated_word)

    # Sanity check that all files now exist.
    _files_exist(filenames_to_write_imgs.values() + filenames_to_write_auds.values())
    logging.info('Wrote media files to: %s', FLAGS.output_dir)

    # Write CSV that can be imported into an Anki deck.
    csv_rows = anki_import_csv.make_csv_format(
        word_translation_pairs.translation_dict,
        filenames_to_write_imgs,
        filenames_to_write_auds,
        extra_info=word_translation_pairs.extra_info)
    # We need to set a custom dialect to avoid double-quoting quotation marks.
    csv.register_dialect('mydialect', delimiter=';', doublequote=False, quotechar='\'')
    with open(FLAGS.output_csv_file, 'w') as csvfile:
        writer = csv.writer(csvfile, dialect='mydialect')
        writer.writerows(csv_rows)
    logging.info('Wrote Anki import csv to: %s', FLAGS.output_csv_file)


if __name__ == "__main__":
    parser = EasyAnkiArgParser()
    FLAGS = parser.parse_args()
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)  # disable annoying warning
    main()

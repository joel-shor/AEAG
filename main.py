'''Main entry point for EasyAnki, the easy way to make Anki flashcards.

The program does the following:
1) Parses a table from disk containing English words and/or foreign words.
2) Translates the English words into a foreign language, and foreign words to English.
3) Finds a representative image from the web or from disk. NOTE: We search images in English, not the translated
 language, for two reasons:
 a) English Image search is better than in most languages
 b) Some languages have specific problems. For instance, in Hebrew, `foreign` and `flower` map to the same word, so
    images for `foreign` are incorrect.
4) Finds a native speaker audio file for the word, from the web or from disk.
5) Writes everything to a target directory.
6) Writes a CSV with the card info that can be imported into an Anki deck.
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

    # Arguments controlling media behavior.
    self.add_argument(
        '--already_downloaded_media_dir',
        default='',
        help='If non-empty, looks for appropriately named media in this folder (images and audio) instead of trying to '
             'download them.')
    self.add_argument(
        '--disable_image_fetching',
        action='store_true',
        help='If `True`, don\'t fetch or copy images. Images pose a difficult semantic problem, since top image '
             'search results are often pop-culture references, and not really what we want.'
             'NOTE: we still write image file locations to the Anki import CSV, but we can simply ignore it on import.')
    self.add_argument(
        '--override_images',
        action='store_true',
        help='If `True`, copy over already existing images.')

    # Output arguments.
    self.add_argument(
        '--output_dir',
        default='',
        help='The directory where the files will be written to disk. This will often be Anki\'s media folder.')
    self.add_argument(
        '--output_csv_file',
        default='',
        help='The location of the Anki import csv file to generate.')

    # Debug arguments.
    self.add_argument(
        '--log',
        default='WARNING',
        help='The level of logging to display ex INFO or DEBUG.')



NUM_INPUT_FILE_FIELDS = 3
IMAGE_FILENAME_FORMAT = '{english}.png'  # image filename to write
AUDIO_FILENAME_FORMAT = '{translation}.mp3'  # audio filename to write

class WordTranslationPairs(object):
    """A thin wrapper around a list of tuples."""
    def __init__(self, tuple_list, english_index=0, translation_index=1):
        self._english_index = english_index
        self._translation_index = translation_index
        self._tuple_list = self._normalize_tuple_list(tuple_list)

    def _normalize_tuple_list(self, tuple_list):
        """Make sure that tuples have the right number of elements."""
        new_tuple_list = []
        for tpl in tuple_list:
            if len(tpl) != NUM_INPUT_FILE_FIELDS:
                if len(tpl) == 2:
                    # If we just have a word and a translation, make the rest
                    # empty strings.
                    new_tpl = [""] * NUM_INPUT_FILE_FIELDS
                    new_tpl[self._english_index] = tpl[self._english_index]
                    new_tpl[self._translation_index] = tpl[
                        self._translation_index]
                    tpl = tuple(new_tpl)
                else:
                    raise ValueError(
                        "Tuple %s had %i fields instead of the expected "
                        "number: %i" % (tpl, len(tpl), NUM_INPUT_FILE_FIELDS))
            assert len(tpl) == NUM_INPUT_FILE_FIELDS
            new_tuple_list.append(tpl)
        return new_tuple_list

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
        return {x[self._english_index]: x[self._translation_index] for x in
                self.data}

    def get_translation(self, english_word):
        return self.translation_dict[english_word]

    @property
    def reverse_translation_dict(self):
        return {x[self._translation_index]: x[self._english_index] for x in
                self.data}

    def get_english(self, translated_word):
        return self.reverse_translation_dict[translated_word]

    @property
    def extra_info(self):
        extra_info_indices = range(NUM_INPUT_FILE_FIELDS)
        extra_info_indices.remove(self._english_index)
        extra_info_indices.remove(self._translation_index)
        if extra_info_indices:
            return {x[self._english_index]: [x[i] for i in extra_info_indices]
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
            raise ValueError('Tried to deleted translated word `%s`, but '
                             'couldn\'t find it in the word list.' %
                             translated_word)
        del self._tuple_list[index]


def _num_elements_in_first_row(input_filename, delimiter=","):
    """Parses input file and returns a `WordTranslationPairs`."""
    with open(input_filename, 'r') as f:
        lines = f.readlines()
    reader = csv.reader(lines, delimiter=delimiter, doublequote=True)
    return sum([x != '' for x in reader.next()])


def parse_word_translation_csv(input_filename, delimiter=","):
    """Parses input file and returns a `WordTranslationPairs`."""
    with open(input_filename, 'r') as f:
        lines = f.readlines()
    reader = csv.reader(lines, delimiter=delimiter, doublequote=True)
    word_translation_pairs = [row for row in reader]
    return WordTranslationPairs(word_translation_pairs)


def parse_single_word_csv(input_filename):
    with open(input_filename, 'r') as f:
        lines = f.readlines()
    reader = csv.reader(lines, doublequote=True)
    single_word = [row for row in reader]
    for word in single_word:
        if len(word) > 1:
            raise ValueError('Malformed input: %s' % word)
    return [x[0] for x in single_word]


def _files_exist(filename_list):
    for filename in filename_list:
        if not os.path.exists(filename):
            raise ValueError('`%s` should have existed, but it doesn\'t.' %
                             filename)


def _remove_words(english_words_to_remove, filenames_to_write_auds,
                  filenames_to_write_imgs, word_translation_pairs):
    for english_word in english_words_to_remove:
        translated_word = word_translation_pairs.get_translation(english_word)
        if translated_word in filenames_to_write_auds:
            del filenames_to_write_auds[translated_word]
        if english_word in filenames_to_write_imgs:
            del filenames_to_write_imgs[english_word]
        word_translation_pairs.remove_translated_word(translated_word)


def remove_existing_filenames(full_filenames, target_dir):
    """Removes arguments corresponding to media that already exists.

    Args:
        full_filenames: A dictionary of {word: filenames}.
        target_dir: The directory to check for name collisions.

    Raises:
        ValueError: If any file in `target_dir` has the same basename as any
            files in `full_filenames`.
    """
    basenames = {k: os.path.basename(v) for k, v in full_filenames.items()}
    for word, basename in basenames.items():
        if os.path.isfile(os.path.join(target_dir, basename)):
            del full_filenames[word]
            logging.info('%s already exists, so removing %s from current '
                         'search.' % (basename, word))


def _write_csv_rows(csv_rows, output_csv_file):
    # We need to set a custom dialect to avoid double-quoting quotation marks.
    csv.register_dialect(
        'mydialect', delimiter=';', doublequote=False, quotechar='\'')
    with open(output_csv_file, 'w') as csvfile:
        writer = csv.writer(csvfile, dialect='mydialect')
        writer.writerows(csv_rows)


def _check_unique(translated_words_no_diacritics):
    for i, w in enumerate(translated_words_no_diacritics[1:]):
        if w in translated_words_no_diacritics[:i+1]:
            raise ValueError('`%s` is duplicated in translations.' % w)


def _all_unique(word_list):
    return len(word_list) == len(set(word_list))


def main(argv=None):
    del argv

    # Parse input CSV file. Infer the expected format by peaking at the number
    # of elements in the first line.
    if _num_elements_in_first_row(FLAGS.input_file) == 1:
        single_words = parse_single_word_csv(FLAGS.input_file)
        english_words, translated_words = translate_lib.get_translations(
            single_words, credentials)
        logging.info('Translated %i words.' % len(translated_words))
        translated_words_no_diacritics = translate_lib.strip_diacritics(
            translated_words)
        _check_unique(translated_words_no_diacritics)
        word_translation_pairs = WordTranslationPairs(
            zip(english_words, translated_words_no_diacritics,
                translated_words))
    else:
        word_translation_pairs = parse_word_translation_csv(FLAGS.input_file)
    assert isinstance(word_translation_pairs, WordTranslationPairs)
    if not _all_unique(word_translation_pairs.english_words):
        raise ValueError('Not all words are unique.')
    if not _all_unique(word_translation_pairs.translations):
        raise ValueError('Not all translations are unique.')

    # Determine full filename where media should be written to.
    # If the media is already fetched, we still want to write it to the CSV, but
    # we don't want to fetch it.
    filenames_to_write_imgs = {
        word: os.path.join(FLAGS.output_dir, IMAGE_FILENAME_FORMAT.format(
            english=word)) for word in word_translation_pairs.english_words}
    filenames_to_write_auds = {
        word: os.path.join(FLAGS.output_dir, AUDIO_FILENAME_FORMAT.format(
            translation=word)) for word in word_translation_pairs.translations}

    # The media we write might be different than the media that we fetch, if
    # some media already exists. Make a copy
    # of the media list so we can track media to fetch, and remove entries
    # corresponding to media that already exists.
    if FLAGS.disable_image_fetching:
        filenames_to_fetch_imgs = {}
    else:
        filenames_to_fetch_imgs = {k: v for k, v in filenames_to_write_imgs.items()}
    filenames_to_fetch_auds = {k: v for k, v in filenames_to_write_auds.items()}
    # NOTE: This function modifies the first argument.
    if not FLAGS.override_images:
        remove_existing_filenames(filenames_to_fetch_imgs, FLAGS.output_dir)
    remove_existing_filenames(filenames_to_fetch_auds, FLAGS.output_dir)

    # Get images, and audio.
    # TODO(joelshor): Try to combine approaches and fetch media if it doesn't
    # exist.
    if FLAGS.already_downloaded_media_dir:
        images_lib.copy_images_from_disk(
            filenames_to_fetch_imgs, FLAGS.already_downloaded_media_dir)
        audio_lib.copy_audio_from_disk(
            filenames_to_fetch_auds, FLAGS.already_downloaded_media_dir)
    else:
        words_without_imgs = images_lib.get_images(
            filenames_to_fetch_imgs, credentials)
        words_without_audio = audio_lib.get_audio(
            filenames_to_fetch_auds, credentials)

        # Remove words without audio or image from flashcard list *to write to
        # csv*.
        for english_word in words_without_imgs:
            translated_word = word_translation_pairs.get_translation(
                english_word)
            logging.warning('Couldn\'t find image for: %s / %s', english_word,
                            translated_word)
        for translated_word in words_without_audio:
            english_word = word_translation_pairs.get_english(translated_word)
            logging.warning('Couldn\'t find audio for:  %s / %s', english_word,
                            translated_word)
        english_words_to_remove = set(words_without_imgs).union(
            set([word_translation_pairs.get_english(x) for x in words_without_audio]))
        _remove_words(english_words_to_remove, filenames_to_write_auds,
                      filenames_to_write_imgs, word_translation_pairs)

    # Sanity check that all files now exist.
    if not FLAGS.disable_image_fetching:
        _files_exist(filenames_to_write_imgs.values())
    _files_exist(filenames_to_write_auds.values())
    logging.info('Wrote media files to: %s', FLAGS.output_dir)

    # Write CSV that can be imported into an Anki deck.
    csv_rows = anki_import_csv.make_csv_format(
        word_translation_pairs.translation_dict,
        filenames_to_write_imgs,
        filenames_to_write_auds,
        extra_info=word_translation_pairs.extra_info)
    _write_csv_rows(csv_rows, FLAGS.output_csv_file)
    logging.warning('Wrote Anki import csv to: %s', FLAGS.output_csv_file)


def set_logging_level(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(level=numeric_level)


if __name__ == "__main__":
    parser = EasyAnkiArgParser()
    FLAGS = parser.parse_args()
    logging.getLogger('googleapiclient.discovery_cache').setLevel(
        logging.ERROR)  # disable annoying warning
    set_logging_level(FLAGS.log)
    main()

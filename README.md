# NEAG (aNother Easy Anki Generator)

By shor.joel@gmail.com (Joel Shor)
## Intro

This project generates Anki flashcards for language learning. Some sources suggest that the
the most useful language-learning flashcards only have the target language, images, and audio in the target language
(ex Fluent Forever), and this program generates cards in this style.

This program does the following:

####Input:

1) A CSV of English words

####Actions:

1) Translates words to target language
1) Performs extra behavior (like stripping diacritics, if necessary)
1) Fetches images associated with the word
1) Fetches audio of native speakers reading the translation
1) Writes media files to Anki's media directory
1) Generates a CSV file so Anki can import the words and media

####Outputs:

1) Writes images and audio to the target directory (often the Anki media directory)
1) Writes a CSV file with English, translation, audio, image, and side information

Currently, AEAG does **not** do the following:

1) Actually import the notes into the desired deck.
1) Generate the Anki card layout
1) Set up external API accounts that you might need (Google Cloud account, etc)

## How to use

Before you do anything, check to make sure that the public APIs are as expected. You'll need to
get credentials for these services, or email `shor.joel@gmail.com` to use the author's. Add them to
`credentials.py`.

### Getting and testing credentials

1) Follow the instructions at the top of `images.py` to get Google Custom Search Engine credentials. Information
can be found at "https://developers.google.com/custom-search/".

1) If Google Text-To-Speech doesn't have your desired language, you might need to use Forvo. Go to
"https://www.forvo.com" and sign up to receive a Forvo API key.

Once your credentials are added, check that the APIs are as expected:

```python
python check_public_apis.py
```

### Generating cards

There are two main modes. One does all the above. The second assumes you've already
downloaded the media that you want, and instead just copies them to the target directory
and writes the Anki import CSV. This mode is useful if you've run out of external API quota, or
you want to manually control which media is associated with which card.

To run in the first mode, run:

```python
python main.py \
--input_file=/User/test/words.csv \
--output_dir=/anki/media/folder \
--output_csv_file=/csv/for/anki/to/import
```

If you've already downloaded the media you want, run something like:

```python
python main.py \
--input_file=/User/test/words.csv \
--output_dir=/anki/media/folder \
--output_csv_file=/csv/for/anki/to/import \
--already_downloaded_media_dir=/path/to/downloaded/media
```


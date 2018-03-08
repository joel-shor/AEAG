# Another Easy Anki Generator (AEAG)

This project assists in language learning with Anki by automating the following steps:

1) Translates English word
1) Performs extra behavior (like stripping diacritics, if necessary)
1) Fetches images associated with vocabulary
1) Fetches audio of native speakers reading vocabulary
1) Writing media files to Anki's media directory
1) Generating a csv file so Anki can import the words and media

Currently, AEAG does **not** do the following:

1) Actually import the notes into the desired deck.

Since public APIs change all the time, be sure to run the following to check that
the translating/image fetching/audio fetching all works properly:

```python
python check_public_apis.py
```

Then run something like: 

```python
python main.py --already_downloaded_media_dir='' --ignore_if_media_already_exits
```
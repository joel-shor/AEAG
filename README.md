# Another Easy Anki Generator (AEAG)

This project assists in language learning by automating the following steps:

1) Translates English word to Hebrew
1) Strips diacritics, if necessary
1) Fetches images associated with vocabulary
1) Fetches audio of native speakers reading vocabulary
1) Writing media files to Anki's media directory
1) Generating a csv file so Anki can import the words and media

Currently, AEAG does **not** do the following:

1) Actually import the notes into the desired deck.

Note that word translation can be done easily in google spreadsheets using the function `=GOOGLETRANSLATE(B128, "en", "he")`.
"""Contains credentials for accessing third-party APIs."""

__author__ = 'shor.joel@gmail.com (Joel Shor)'


class Credentials(object):
    """A hierarchical class for external API credentials."""
    pass



credentials = Credentials()

######### CUSTOM IMAGE SEARCH CREDENTIALS ###############
credentials.images = Credentials()

# From https://console.developers.google.com/apis/credentials
credentials.images.developerKey = ''

# Search Engine ID, from https://cse.google.com/cse/all.
credentials.images.cxString = ''

######### CUSTOM AUDIO SEARCH CREDENTIALS ###############
credentials.audio = Credentials()

credentials.audio.yandexKey = ''

credentials.audio.forvoAPIKey = ''

######### TRANSLATION CREDENTIALS ###############
credentials.translate = Credentials()

# Same as `credentials.images.developerKey` above.
credentials.translate.developerKey = credentials.images.developerKey
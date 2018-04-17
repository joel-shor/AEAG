"""Contains credentials for accessing third-party APIs."""

__author__ = 'shor.joel@gmail.com (Joel Shor)'


class Credentials(object):
    """A hierarchical class for external API credentials."""
    pass



credentials = Credentials()

######### CUSTOM IMAGE SEARCH CREDENTIALS ###############
credentials.images = Credentials()

# From https://console.developers.google.com/apis/credentials
credentials.images.developerKey = 'AIzaSyCLUXhz2TGKs_4JZ12xPgyBXwgfvD13zz8'

# Search Engine ID, from https://cse.google.com/cse/all.
credentials.images.cxString = '005399444954916912786:zcgsandx3je'

######### CUSTOM AUDIO SEARCH CREDENTIALS ###############
credentials.audio = Credentials()

credentials.audio.yandexKey = 'trnsl.1.1.20180227T013535Z.cbdfcefc9e1e1fdd.6b6330f93a6ecf082b57c13fac030c7143dc0d12'

credentials.audio.forvoAPIKey = '35a886e44bd9d1a7a46b2f80e3cb3701'

######### TRANSLATION CREDENTIALS ###############
credentials.translate = Credentials()

# Same as `credentials.images.developerKey` above.
credentials.translate.developerKey = credentials.images.developerKey
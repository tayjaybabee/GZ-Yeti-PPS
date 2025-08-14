from platformdirs import PlatformDirs


AUTHOR = 'Inspyre-Softworks'
PROG   = 'GZYetiPPS'

APP_DIRS = PlatformDirs(appname=PROG, appauthor=AUTHOR)

DEFAULT_API_STUB  = 'http://yeti.local'
DEFAULT_CACHE_TTL = 5
DEFAULT_LOG_LEVEL = 'DEBUG'
DEFAULT_STATE_URL = f'{DEFAULT_API_STUB}/state'
DEFAULT_TIMEOUT   = 5
DEFAULT_WIFI_URL  = f'{DEFAULT_API_STUB}/wifi'

TRUE_VALUES = [
    1,
    '1',
    'on',
    'true',
    True,
    'yes',
    'y'
]

FALSE_VALUES = [
    0,
    '0',
    'off',
    'false',
    False,
    'no',
    'n'
]

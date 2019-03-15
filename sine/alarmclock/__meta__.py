#  dP"""8b    ii    88i    88   888888
#  Ib    "    __    88 i   88   88
#   '"~_      88    88  i  88   88888
#      ""b    88    88   i 88   88
#  "booodP    88    88    i88   888888

_VERSION = (0, 7, 2)

DESCRIPTION = 'Windows command line alarm clock (python3)'
URL = 'https://github.com/SineObama/AlarmClock'
VERSION = '.'.join(map(str, _VERSION))
REQUIRED = [
    'pypiwin32',
    'plone.synchronize',
    'sine.threads>=0.1.6',
    'sine.path',
    'sine.properties',
    'sine.event'
]

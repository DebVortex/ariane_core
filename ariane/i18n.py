import gettext as gt
import os

import locale

LANGUAGES = {}
LOCALEDIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')


def _(message):
    """Translate strings on the fly."""
    language = locale.getlocale()[0]
    translate = LANGUAGES.get(language)
    if not translate:
        translate = gt.translation('ariane', LOCALEDIR, fallback=True, languages=[language])
        LANGUAGES[language] = translate
    return translate.gettext(message)


def m_(message):
    """Mark strings as translateable."""
    return message

import pycld2

from ariane.i18n import _

SUPPORTED_LANGUAGES = ["en", "de"]


def check_languages(languages):
    for lang in languages:
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(
                _("Language {lang} not supported. Supported are {supported_languages}").format(
                    **{"lang": lang, "supported_languages": SUPPORTED_LANGUAGES}
                )
            )


def detect_language(text):
    _, _, unsorted_results = pycld2.detect(text, hintLanguageHTTPHeaders='en,de')
    sorted_results = sorted([d for d in unsorted_results], key=lambda x: -x[3])
    return sorted_results[0][1]

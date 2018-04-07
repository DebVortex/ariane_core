import os
from importlib import import_module

import pycld2

from ariane.i18n import _


def get_config():
    config_module = os.environ.get("ARIANE_CONFIG_MODULE", 'ariane.core.config')
    config_class = os.environ.get("ARIANE_CONFIG_CLASS", 'BaseConfig')
    return getattr(import_module(config_module), config_class)()


def check_languages(languages):
    for lang in languages:
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(
                _("Language {lang} not supported. Supported are {supported_languages}").format(
                    **{"lang": lang, "supported_languages": SUPPORTED_LANGUAGES}
                )
            )


def detect_language(text):
    _, _, unsorted_results = pycld2.detect(
        text,
        hintLanguageHTTPHeaders=','.join(SUPPORTED_LANGUAGES)
    )
    sorted_results = sorted([d for d in unsorted_results], key=lambda x: -x[3])
    return sorted_results[0][1]


SUPPORTED_LANGUAGES = get_config().SUPPORTED_LANGUAGES

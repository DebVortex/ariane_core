import os

import click
import pycld2
import importlib
import json
from tempfile import NamedTemporaryFile

from ariane.i18n import _

SUPPORTED_LANGUAGES = ["en", "de"]


def get_base_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_model_base_dir(lang):
    return os.path.join(get_base_path(), "config/{lang}/models/".format(lang=lang))


def get_model_dir(lang):
    model_base_dir = get_model_base_dir(lang)
    return os.path.join(model_base_dir, sorted(os.listdir(model_base_dir))[-1])


def get_config_path(lang):
    return os.path.join(get_base_path(), "config/{lang}/config.json".format(lang=lang))


def get_training_data_path(lang, config):
    training_data = {
        "rasa_nlu_data": {"common_examples": [], "entity_synonyms": [], "regex_features": []},
    }
    for app_name in config['active_apps']:
        click.echo(_("Collecting training data for {app}").format(app=app_name))
        data_path = os.path.join(
            os.path.dirname(importlib.import_module(app_name).__file__),
            'training_data/{lang}/data.json'.format(lang=lang)
        )
        with open(data_path) as str_data:
            data = json.load(str_data)
            training_data["rasa_nlu_data"]["common_examples"] += data.get("common_examples", [])
            training_data["rasa_nlu_data"]["entity_synonyms"] += data.get("entity_synonyms", [])
            training_data["rasa_nlu_data"]["regex_features"] += data.get("regex_features", [])
    with NamedTemporaryFile(delete=False, mode="w", suffix=".json") as training_data_file:
        click.echo("Writing collected data to file {tmp_file}".format(
            tmp_file=training_data_file.name
        ))
        training_data_file.write(json.dumps(training_data))
    return training_data_file.name


def check_languages(languages):
    for lang in languages:
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(
                _("Language {lang} not supported. Supported are {supported_languages}").format(
                    **{"lang": lang, "supported_languages": SUPPORTED_LANGUAGES}
                )
            )


def load_config():
    config_path = os.environ.get('ARIANE_CONFIG_PATH', os.path.join(get_base_path(), "config/config.json"))
    with open(config_path) as config_file:
        config = json.load(config_file)
    return config


def detect_language(text):
    _, _, unsorted_results = pycld2.detect(text, hintLanguageHTTPHeaders='en,de')
    sorted_results = sorted([d for d in unsorted_results], key=lambda x: -x[3])
    return sorted_results[0][1]

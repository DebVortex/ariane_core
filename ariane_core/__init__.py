# -*- coding: utf-8 -*-
"""Top-level package for Ariane Core."""
__author__ = """Max Brauer"""
__email__ = "max@max-brauer.de"
__version__ = "0.1.0"

import datetime
import os
import importlib
import json
from pprint import pprint
import shutil
from tempfile import NamedTemporaryFile

import click
from langdetect import detect
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.converters import load_data
from rasa_nlu.data_router import DataRouter
from rasa_nlu.model import Interpreter, Metadata, Trainer

SUPPORTED_LANGUAGES = ["en", "de"]


def _get_base_path():
    return os.path.dirname(os.path.realpath(__file__))


def _get_model_base_dir(lang):
    return os.path.join(_get_base_path(), "config/{lang}/models/".format(lang=lang))


def _get_model_dir(lang):
    model_base_dir = _get_model_base_dir(lang)
    return os.path.join(model_base_dir, sorted(os.listdir(model_base_dir))[-1])


def _get_config_path(lang):
    return os.path.join(_get_base_path(), "config/{lang}/config.json".format(lang=lang))


def _get_training_data_path(lang, config):
    training_data = {
        "rasa_nlu_data": {"common_examples": [], "entity_synonyms": [], "regex_features": []},
    }
    for app_name in config['active_apps']:
        click.echo("Collecting training data for {app}".format(app=app_name))
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


def _check_languages(languages):
    for lang in languages:
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(
                "Language {lang} not supported. Supported are {supported_languages}".format(
                    **{"lang": lang, "supported_languages": SUPPORTED_LANGUAGES}
                )
            )


def _load_config():
    with open(os.path.join(_get_base_path(), "config/config.json")) as config_file:
        config = json.load(config_file)
    return config


@click.group()
@click.version_option(__version__)
def cli():
    pass


@click.command()
@click.option("languages", "--language", "-l", multiple=True, default=SUPPORTED_LANGUAGES,
    help="Languages to train. Can be used multiple times. "
         "Defaults to {langs}".format(langs=SUPPORTED_LANGUAGES))
def train_models(languages):
    """Generate your trained model."""
    _check_languages(languages)
    config = _load_config()
    for language in languages:
        click.echo("================== Processing {lang} ==================".format(lang=language))
        training_data = load_data(_get_training_data_path(language, config))
        trainer = Trainer(RasaNLUConfig(cmdline_args=config))
        click.echo("Training data for language {lang}.".format(lang=language))
        trainer.train(training_data)
        click.echo("Persisting trained data for {lang}.".format(lang=language))
        model_dir = trainer.persist(_get_model_base_dir(language))
        click.echo("Stored data for {lang} in {path}.".format(lang=language, path=model_dir))
    click.echo("================ Finished Training ================")


@click.command()
@click.option("languages", "--language", "-l", multiple=True, default=SUPPORTED_LANGUAGES,
    help="Languages of which models should be deleted. Can be used multiple times. "
         "Defaults to {langs}""".format(langs=SUPPORTED_LANGUAGES))
def clear_models(languages):
    """Clear trained models."""
    for language in languages:
        click.echo("Processing {lang}.".format(lang=language))
        model_base_dir = _get_model_base_dir(language)
        model_dirs = os.listdir(model_base_dir)
        for model_dir in model_dirs:
            model_path = os.path.join(model_base_dir, model_dir)
            if os.path.isdir(model_path):
                click.echo("Deleting {model_path}.".format(model_path=model_path))
                shutil.rmtree(model_path)


@click.command()
@click.option("--language", "-l", default=None,
    help="Language of the text. If not provided, the language will be guessed.".format(
        langs=SUPPORTED_LANGUAGES
    )
)
@click.argument("text")
def interprete(text, language):
    """Interprete the given text."""
    if not language:
        language = detect(text)
    _check_languages([language])
    metadata = Metadata.load(_get_model_dir(language))
    config_file = _load_config()
    config = RasaNLUConfig(cmdline_args=config_file)
    interpreter = Interpreter.load(metadata, config)
    query_logger = DataRouter._create_query_logger(config['response_log'])
    response = interpreter.parse(text)
    log = {"user_input": response, "time": datetime.datetime.now().isoformat()}
    query_logger.info(json.dumps(log, sort_keys=True))
    click.echo(pprint(response))


cli.add_command(train_models)
cli.add_command(clear_models)
cli.add_command(interprete)

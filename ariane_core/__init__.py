# -*- coding: utf-8 -*-
"""Top-level package for Ariane Core."""
__author__ = """Max Brauer"""
__email__ = "max@max-brauer.de"
__version__ = "0.1.0"

import os
from pprint import pprint
import shutil

import click
from langdetect import detect
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.converters import load_data
from rasa_nlu.model import Interpreter, Metadata, Trainer

SUPPORTED_LANGUAGES = ["en", "de"]
UNSUPPORTED_LANG_MSG = "Language {lang} not supported. Supported are {supported_languages}"


def _get_base_path():
    return os.path.dirname(os.path.realpath(__file__))


def _get_model_base_dir(lang):
    return os.path.join(_get_base_path(), "config/{lang}/models/".format(lang=lang))


def _get_model_dir(lang):
    model_base_dir = _get_model_base_dir(lang)
    return os.path.join(model_base_dir, sorted(os.listdir(model_base_dir))[-1])


def _get_config_path(lang):
    return os.path.join(_get_base_path(), "config/{lang}/config.json".format(lang=lang))


def _get_training_data_path(lang):
    return os.path.join(_get_base_path(), "config/{lang}/training_data.json".format(lang=lang))


def _check_languages(languages):
    for lang in languages:
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(
                UNSUPPORTED_LANG_MSG.format(
                    **{"lang": lang, "supported_languages": SUPPORTED_LANGUAGES}
                )
            )


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
    for language in languages:
        click.echo("Processing {lang}...".format(lang=language))
        training_data = load_data(_get_training_data_path(language))
        trainer = Trainer(RasaNLUConfig(_get_config_path(language)))
        trainer.train(training_data)
        model_dir = trainer.persist(_get_model_base_dir(language))
        click.echo("Stored data for {lang} in {path}.".format(lang=language, path=model_dir))


@click.command()
@click.option("languages", "--language", "-l", multiple=True, default=SUPPORTED_LANGUAGES,
    help="Languages of which models should be deleted. Can be used multiple times. "
         "Defaults to {langs}""".format(langs=SUPPORTED_LANGUAGES))
def clear_models(languages):
    """Clear trained models."""
    for language in languages:
        click.echo("Processing {lang}...".format(lang=language))
        model_base_dir = _get_model_base_dir(language)
        model_dirs = os.listdir(model_base_dir)
        for model_dir in model_dirs:
            model_path = os.path.join(model_base_dir, model_dir)
            if os.path.isdir(model_path):
                click.echo("Deleting {model_path}...".format(model_path=model_path))
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
    interpreter = Interpreter.load(metadata, RasaNLUConfig(_get_config_path(language)))
    click.echo(pprint(interpreter.parse(text)))


cli.add_command(train_models)
cli.add_command(clear_models)
cli.add_command(interprete)

# -*- coding: utf-8 -*-

import os
import shutil

import click
from langdetect import detect
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.converters import load_data
from rasa_nlu.model import Trainer

from . import Ariane
from . import utils

from ..i18n import _
from .. import __version__


@click.group()
@click.version_option(__version__)
def main():
    pass


@click.command()
@click.option("languages", "--language", "-l", multiple=True, default=utils.SUPPORTED_LANGUAGES,
    help="Languages to train. Can be used multiple times. "
         "Defaults to {langs}".format(langs=utils.SUPPORTED_LANGUAGES))
def train_models(languages):
    """Generate your trained model."""
    utils.check_languages(languages)
    config = utils.load_config()
    for language in languages:
        click.echo(_("================== Processing {lang} ==================").format(lang=language))
        training_data = load_data(utils.get_training_data_path(language, config))
        trainer = Trainer(RasaNLUConfig(cmdline_args=config))
        click.echo(_("Training data for language {lang}.").format(lang=language))
        trainer.train(training_data)
        click.echo(_("Persisting trained data for {lang}.").format(lang=language))
        model_dir = trainer.persist(utils.get_model_base_dir(language))
        click.echo(_("Stored data for {lang} in {path}.").format(lang=language, path=model_dir))
    click.echo(_("================ Finished Training ================"))


@click.command()
@click.option("languages", "--language", "-l", multiple=True, default=utils.SUPPORTED_LANGUAGES,
    help="Languages of which models should be deleted. Can be used multiple times. "
         "Defaults to {langs}""".format(langs=utils.SUPPORTED_LANGUAGES))
def clear_models(languages):
    """Clear trained models."""
    for language in languages:
        click.echo(_("Processing {lang}.").format(lang=language))
        model_base_dir = utils.get_model_base_dir(language)
        model_dirs = os.listdir(model_base_dir)
        for model_dir in model_dirs:
            model_path = os.path.join(model_base_dir, model_dir)
            if os.path.isdir(model_path):
                click.echo(_("Deleting {model_path}.").format(model_path=model_path))
                shutil.rmtree(model_path)


@click.command()
@click.option("--language", "-l", default=None,
    help="Language of the text. If not provided, the language will be guessed.")
@click.argument("text")
def interprete(text, language):
    """Interprete the given text."""
    if not language:
        language = detect(text)
    ariane = Ariane(language)
    response = ariane.interprete(text)
    click.echo(response)


@click.command()
@click.option("--language", "-l", default=None,
    help="Language of the text. If not provided, the language will be guessed.")
@click.argument("text")
def handle(text, language):
    """Interprete and handle the given text."""
    if not language:
        language = detect(text)
    ariane = Ariane(language)
    response = ariane.handle(text)
    click.echo(response)


main.add_command(train_models)
main.add_command(clear_models)
main.add_command(interprete)
main.add_command(handle)

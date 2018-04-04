# -*- coding: utf-8 -*-
import asyncio
import os
import shutil

import click


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
    raise NotImplemented("Under construction. Code is being portet to snips.")


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
        language = utils.detect_language(text)
    ariane = Ariane([language])
    response = ariane.interprete(text, language)
    click.echo(response)


@click.command()
@click.option("--language", "-l", default=None,
    help="Language of the text. If not provided, the language will be guessed.")
@click.argument("text")
def handle(text, language):
    """Interprete and handle the given text."""
    if not language:
        language = utils.detect_language(text)
    ariane = Ariane([language])
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(ariane.handle(text, language)))
    loop.close()


main.add_command(train_models)
main.add_command(clear_models)
main.add_command(interprete)
main.add_command(handle)

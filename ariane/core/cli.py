# -*- coding: utf-8 -*-
import asyncio
from importlib import import_module
import os
from subprocess import Popen, PIPE

from time import gmtime, strftime

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
    config = utils.get_config()
    for language in languages:
        click.echo("Processing language {lang}.".format(lang=language))
        intent_files, entity_files = [], []
        for app_module in config.ACTIVE_APPS:
            click.echo("Collecting data for {app_module}".format(app_module=app_module))
            app = import_module(app_module)
            app_dir = os.path.dirname(app.__file__)
            data_path = os.path.join(app_dir, 'data', language)
            training_data = os.path.join(data_path, 'training_data')
            entity_data = os.path.join(data_path, 'entity_data')
            if os.path.isdir(data_path):
                click.echo("Collecting training data.")
                if os.path.isdir(training_data):
                    for training_file in os.listdir(training_data):
                        intent_files.append(os.path.join(training_data, training_file))
                click.echo("Collecting entity data.")
                if os.path.isdir(entity_data):
                    for entity in os.listdir(entity_data):
                        entity_files.append(os.path.join(entity_data, entity))
        if not intent_files:
            click.echo("No training data found. Skipping...")
            continue
        model_file_name = strftime("model_%Y_%m_%d_%H_%M_%S.json", gmtime())
        model_file = os.path.join(config.MODEL_BASE_DIR, language, model_file_name)
        cmd = ['generate-dataset', '--language', language, '--intent-files', *intent_files]
        if entity_files:
            cmd = cmd + ['--entity-files', *entity_files]
        process = Popen(cmd, stdout=PIPE)
        status_code = process.wait()
        stdout, stderr = process.communicate()
        if status_code == 0:
            with open(model_file, 'wb') as mf:
                mf.write(stdout)
                click.echo("Generated model for {lang} in {model_file}.".format(lang=language, model_file=model_file))


@click.command()
@click.option("languages", "--language", "-l", multiple=True, default=utils.SUPPORTED_LANGUAGES,
    help="Languages of which models should be deleted. Can be used multiple times. "
         "Defaults to {langs}""".format(langs=utils.SUPPORTED_LANGUAGES))
def clear_models(languages):
    """Clear trained models."""
    config = utils.get_config()
    for language in languages:
        click.echo(_("Processing {lang}.").format(lang=language))
        lang_dir = os.path.join(config.MODEL_BASE_DIR, language)
        if os.path.exists(lang_dir):
            for model_file in os.listdir(lang_dir):
                if not model_file.startswith("."):
                    model = os.path.join(lang_dir, model_file)
                    click.echo(_("Removing model {model}.".format(model=model)))
                    os.remove(model)
        else:
            click.echo(_("Dir {lang_dir} not found.".format(lang_dir=lang_dir)))


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

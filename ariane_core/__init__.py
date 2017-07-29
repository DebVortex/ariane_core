# -*- coding: utf-8 -*-
"""Top-level package for Ariane Core."""
__author__ = """Max Brauer"""
__email__ = 'max@max-brauer.de'
__version__ = '0.1.0'

SUPPORTED_LANGUAGES = ['en', 'de']

import click


@click.group()
@click.version_option(__version__)
def cli():
    pass


@click.command()
@click.option('--languages', '-l', multiple=True, default=SUPPORTED_LANGUAGES,
    help='Languages to train. Defaults to {langs}'.format(
        langs=SUPPORTED_LANGUAGES
    )
)
def train(languages):
    """Generate your trained model."""
    for lang in languages:
        if lang in SUPPORTED_LANGUAGES:
            click.echo("Processing {lang}...".format(lang=lang))
        else:
            click.echo("{lang} not supported. Skipping...".format(lang=lang))


cli.add_command(train)

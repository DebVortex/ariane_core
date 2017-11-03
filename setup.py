#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "aiohttp==2.3.1",
    "click==6.7",
    "langdetect==1.0.7",
    "py-translate==1.0.3",
    "rasa-nlu==0.9.1",
    "scikit-learn==0.18.2",
    "scipy==0.19.1",
    "six==1.10.0",
    "sklearn-crfsuite==0.3.6",
    "spacy==1.9.0",
]

setup_requirements = [
    # TODO(DebVortex): put setup requirements (distutils extensions, etc.) here
]

extras_require = {
    'test': [
        'pytest==3.2.2',
        'flake8==3.4.1',
        'coverage==4.4.1'
    ],
    'development': [
        'transifex-client==0.12.4'
    ]
}

setup(
    name='ariane',
    version='0.1.0',
    description="",
    long_description=readme + '\n\n' + history,
    author="Max Brauer",
    author_email='max@max-brauer.de',
    url='https://github.com/DebVortex/ariane',
    packages=find_packages(include=['ariane']),
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='ariane',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Natural Language :: German',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    extras_require=extras_require,
    setup_requires=setup_requirements,
    entry_points='''
        [console_scripts]
        ariane=ariane.core.cli:main
    ''',
)

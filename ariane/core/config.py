import os

import json

import ariane


class BaseConfig:
    BASE_DIR = os.path.dirname(ariane.__file__)

    SUPPORTED_LANGUAGES = ['en', 'de']
    MODEL_BASE_DIR = os.path.join(BASE_DIR, 'core', 'models')

    ACTIVE_APPS = [
        'ariane.apps.weather',
        'ariane.apps.knowledge_base'
    ]

    @property
    def SNIPS_CONFIG_DE(self):
        return self.get_snips_config('de')

    @property
    def SNIPS_CONFIG_EN(self):
        return self.get_snips_config('en')

    def get_snips_config(self, lang):
        config_path = 'core/snips_config/config_{lang}.json'.format(lang=lang)
        config_full_path = os.path.join(self.BASE_DIR, config_path)
        with open(config_full_path, 'r') as config_file:
            return json.load(config_file)

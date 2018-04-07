import datetime
import json

from importlib import import_module

import os
from glob import glob

import snips_nlu


from . import utils


class Ariane:

    def __init__(self, languages):
        utils.check_languages(languages)

        config = utils.get_config()

        self.languages = languages
        self.registry = IntentRegistry(config.ACTIVE_APPS)
        self._interpreter = {}
        for language in languages:
            models = os.path.join(config.MODEL_BASE_DIR, language, '*.json')
            model_files = glob(models)
            if model_files:
                model_file_path = model_files[0]
                with open(model_file_path, 'r') as model_file:
                    model = json.load(model_file)
                    snips_nlu.load_resources(language)
                    self._interpreter[language] = snips_nlu.SnipsNLUEngine.from_dict(model)
            else:
                raise FileNotFoundError("Model for language {lang} not found.".format(lang=language))

    def interprete(self, text, lang):
        response = self._interpreter[lang].parse(text)
        return response

    async def handle(self, text, lang):
        response = self.interprete(text, lang)
        return await self.registry(response, lang)


class IntentRegistry:
    _intents = {}

    def __init__(self, apps):
        for app in apps:
            import_module(app)

    def __call__(self, response, language):
        return self._intents[response['intent']['intentName']](response, language)

    @classmethod
    def register(cls, intent):
        def _inner(func):
            cls._intents[intent] = func
            return func
        return _inner

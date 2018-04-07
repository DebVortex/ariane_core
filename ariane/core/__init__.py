import datetime
import json

from importlib import import_module

from . import utils


class Ariane:

    def __init__(self, languages):
        utils.check_languages(languages)

        config = utils.get_config()

        self.languages = languages
        self.registry = IntentRegistry(config.ACTIVE_APPS)
        self._interpreter = {}

    def interprete(self, text, lang):
        raise NotImplementedError("Under construction. Code is being portet to snips.")
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
        return self._intents[response['intent']['name']](response, language)

    @classmethod
    def register(cls, intent):
        def _inner(func):
            cls._intents[intent] = func
            return func
        return _inner

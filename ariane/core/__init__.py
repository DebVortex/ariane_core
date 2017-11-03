import datetime
import json

from importlib import import_module

from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.data_router import DataRouter
from rasa_nlu.model import Interpreter, Metadata

from . import utils


class Ariane:

    def __init__(self, languages):
        utils.check_languages(languages)

        self.languages = languages
        self.config = RasaNLUConfig(cmdline_args=utils.load_config())
        self.query_logger = DataRouter._create_query_logger(self.config['response_log'])
        self._metadata = {}
        self._interpreter = {}
        for lang in languages:
            self._metadata[lang] = Metadata.load(utils.get_model_dir(lang))
            self._interpreter[lang] = Interpreter.load(self._metadata[lang], self.config)
        self.registry = IntentRegistry(self.config['active_apps'])

    def interprete(self, text, lang):
        response = self._interpreter[lang].parse(text)
        log = {"user_input": response, "time": datetime.datetime.now().isoformat()}
        self.query_logger.info(json.dumps(log, sort_keys=True))
        return response

    async def handle(self, text, lang, future):
        response = self.interprete(text, lang)
        return await self.registry(response, lang, future)


class IntentRegistry:
    _intents = {}

    def __init__(self, apps):
        for app in apps:
            import_module(app)

    def __call__(self, response, language, future):
        return self._intents[response['intent']['name']](response, language, future)

    @classmethod
    def register(cls, intent):
        def _inner(func):
            cls._intents[intent] = func
            return func
        return _inner

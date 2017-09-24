import datetime
import json

from importlib import import_module

from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.data_router import DataRouter
from rasa_nlu.model import Interpreter, Metadata, Trainer

from . import utils


class Ariane:

    def __init__(self, language):
        utils.check_languages([language])

        self.language = language
        self.config = RasaNLUConfig(cmdline_args=utils.load_config())
        self._metadata = Metadata.load(utils.get_model_dir(language))
        self._interpreter = Interpreter.load(self._metadata, self.config)
        self.query_logger = DataRouter._create_query_logger(self.config['response_log'])
        self.registry = IntentRegistry(self.config['active_apps'])

    def interprete(self, text):
        response = self._interpreter.parse(text)
        log = {"user_input": response, "time": datetime.datetime.now().isoformat()}
        self.query_logger.info(json.dumps(log, sort_keys=True))
        return response

    def handle(self, text):
        response = self.interprete(text)
        return self.registry(response, self.language)


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

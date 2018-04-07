import os


class BaseConfig:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    SUPPORTED_LANGUAGES = ['de', 'en']
    MODEL_BASE_DIR = os.path.join(BASE_DIR, 'core', 'models')

    ACTIVE_APPS = [
        'ariane.apps.weather',
        'ariane.apps.knowledge_base'
    ]

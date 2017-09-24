import os

import requests
from translate.translator import translator

from ariane.core import IntentRegistry

from . import constants
from ...i18n import gettext as _

# Replace with proper localization
NO_LOCATION = _("For what Place do you want to know the weather?")

# Replace with proper localization
RETURN_TEXT = _('In {location} it is {condition} with {temperature} °C.')


class WeatherClient:

    def __init__(self, api_key):
        self.api_key = api_key

    def get_current_weather(self, location):
        return requests.get(
            'https://api.openweathermap.org/data/2.5/weather',
            params={'q': location, 'APPID': self.api_key, 'units': 'metric'}
        ).json()


@IntentRegistry.register('weather')
def weather(nlu_response, language):
    api_key = os.environ.get('OPEN_WEATHER_MAP_KEY')
    if not api_key:
        raise ValueError(_('No OpenWeatherMap ApiKey provided.'
            ' Please add OPEN_WEATHER_MAP_KEY environment variable'))
    weather_client = WeatherClient(api_key)
    location = None
    for entity in nlu_response['entities']:
        if entity['entity'] == 'GPE':
            location = entity['value']
    if location:
        weather_resp = weather_client.get_current_weather(location)
        condition = constants.WEATHER_DESCRIPTON[weather_resp['weather'][0]['id']]
        if language != 'en':
            # Replace with translation using localization
            condition = translator('en', 'de', condition)[0][0][0]
        response = RETURN_TEXT[language].format(
            location=location,
            temperature=weather_resp['main']['temp'],
            condition=condition
        )
    else:
        response = NO_LOCATION[language]
    return response

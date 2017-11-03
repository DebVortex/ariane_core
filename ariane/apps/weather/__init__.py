import os
import locale

import aiohttp

from ariane.core import IntentRegistry

from . import constants

from ...i18n import m_, _

# Replace with proper localization
NO_LOCATION = m_("For what Place do you want to know the weather?")

# Replace with proper localization
RETURN_TEXT = m_('In {location} it is {condition} with {temperature} °C.')


class WeatherClient:
    weather_url = 'https://api.openweathermap.org/data/2.5/weather'

    def __init__(self, api_key):
        self.api_key = api_key

    async def get_current_weather(self, location):
        params = {'q': location, 'APPID': self.api_key, 'units': 'metric'}
        async with aiohttp.ClientSession() as session:
            async with await session.get(self.weather_url, params=params) as resp:
                return await resp.json()


@IntentRegistry.register('weather')
async def weather(nlu_response, language, future):
    locale.setlocale(locale.LC_ALL, constants.LOCALES[language])
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
        weather_resp = await weather_client.get_current_weather(location)
        response = _(RETURN_TEXT).format(
            location=location,
            temperature=weather_resp['main']['temp'],
            condition=_(constants.WEATHER_DESCRIPTON[weather_resp['weather'][0]['id']])
        )
    else:
        response = _(NO_LOCATION)
    future.set_result(response)

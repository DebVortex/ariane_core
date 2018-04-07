import wikipedia

from ariane.core import IntentRegistry


@IntentRegistry.register('wolfram')
async def wolfram(nlu_response, language):
    raise NotImplementedError("Under construction. Code is being portet to snips.")


@IntentRegistry.register('wiki')
async def wiki(nlu_response, language):
    wikipedia.set_lang(language)
    query = nlu_response['entities'][-1]['value']
    return wikipedia.summary(query, sentences=3)

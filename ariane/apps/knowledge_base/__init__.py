import wikipedia

from ariane.core import IntentRegistry

from ...i18n import m_, _


@IntentRegistry.register('knowledge_base_wolfram')
async def wolfram(nlu_response, language):
    raise NotImplemented()


@IntentRegistry.register('knowledge_base_wiki')
async def wiki(nlu_response, language):
    wikipedia.set_lang(language)
    query = nlu_response['entities'][-1]['value']
    return wikipedia.summary(query, sentences=3)

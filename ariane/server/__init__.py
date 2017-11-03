import asyncio
import aiohttp
from aiohttp import web
import signal
import sys
import json

from langdetect import detect

from ariane.core import Ariane
from ariane.core.utils import load_config, SUPPORTED_LANGUAGES


class ArianeServer(web.Application):

    def __init__(self, loop=None, langs=None):
        super().__init__(loop=loop)
        if not langs:
            self.langs = SUPPORTED_LANGUAGES
        print("Loading following lanugage models: {langs}".format(langs=', '.join(self.langs)))
        self._handler = Ariane(self.langs)
        self.router.add_route('GET', '/', self.handle)

    async def handle(self, request):
        language = request.GET.get('language')
        text = request.GET.get('q')
        if not language:
            language = detect(text)
        future = asyncio.Future()
        await self._handler.handle(text, language, future)
        body = json.dumps(future.result()).encode('utf-8')
        return web.Response(body=body, content_type="application/json")


def run_server(host=None, port=None):
    config = load_config()
    if not host:
        host = config.get('server_host', "127.0.0.1")
    if not port:
        port = config.get('server_port', 8000)
    loop = asyncio.get_event_loop()
    app = ArianeServer(loop=loop)

    def shutdown_signal_handler(signal, frame):
        print("Shutdown received...")
        loop.stop()
        print("Server stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_signal_handler)

    server = loop.create_server(app.make_handler(), host, port)
    print("Server started at {host}:{port}".format(host=host, port=port))
    loop.run_until_complete(server)
    loop.run_forever()


if __name__ == '__main__':
    run_server()

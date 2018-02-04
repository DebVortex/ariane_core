import asyncio
import aiohttp
from aiohttp import web
import os
import signal
import sys
import json

from ariane.core import Ariane
from ariane.core.utils import load_config, detect_language, SUPPORTED_LANGUAGES


class ArianeServer(web.Application):
    _index_tmpl = None

    def __init__(self, loop=None, langs=None):
        super().__init__(loop=loop)
        if not langs:
            self.langs = SUPPORTED_LANGUAGES
        print("Loading following lanugage models: {langs}".format(langs=', '.join(self.langs)))
        self._handler = Ariane(self.langs)
        self.router.add_route('GET', '/', self.index)
        self.router.add_route('POST', '/api', self.api)
        self.router.add_static('/static/', os.path.join(os.path.dirname(__file__), 'static'))

    async def index(self, request):
        tmpl_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        with open(tmpl_path) as tmpl_file:  # repalce with async code
            index_tmpl = tmpl_file.read()
        return web.Response(body=index_tmpl, content_type="text/html")

    async def api(self, request):
        data = await request.post()
        language = data.get('language')
        query = data.get('q')
        if not language:
            language = detect_language(query)
        resp = await self._handler.handle(query, language)
        body = json.dumps(resp).encode('utf-8')
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

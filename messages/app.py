from pathlib import Path

import aiohttp_cors
from aiohttp import web

from .routes import setup_routes


def get_app(config):
    parent = Path(__file__).parent
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
    })

    app['config'] = {}
    app.name = parent.name
    app['config'].update(config)
    setup_routes(app)
    for route in list(app.router.routes()):
        cors.add(route)
    return app

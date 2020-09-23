import asyncio
from importlib import import_module

import click
from aiohttp import web

from _root import init_db
from _root.db import close_mysql, close_queue, init_mysql, init_queue
from _root.settings import get_real_config


def plugin_app(app, prefix, nested):
    async def set_db(a):
        for key, value in a.items():
            nested[key] = value
    app.on_startup.append(set_db)
    app.add_subapp(prefix, nested)


plugins = [
    ('messages', '/messages/'),
]


def load_plugins(root):
    for application_name, prefix in plugins:
        application_module = import_module(f'{application_name}.app')
        application = application_module.get_app(root['config'])
        plugin_app(root, prefix, application)


@click.group()
@click.option('--config')
@click.pass_context
def cli(ctx, config):
    ctx.ensure_object(dict)
    app = web.Application()
    app.name = 'main'

    app['config'] = get_real_config('messages.yaml', config)
    app.on_startup.append(init_mysql)
    app.on_startup.append(init_queue)

    app.on_cleanup.append(close_mysql)
    app.on_cleanup.append(close_queue)

    load_plugins(app)
    ctx.obj['APP'] = app


@cli.command()
@click.pass_context
def create_db(ctx):
    app = ctx.obj['APP']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db.main(app))


@cli.command()
@click.option('--port', type=click.INT, default=3000)
@click.pass_context
def run(ctx, port):
    web.run_app(ctx.obj['APP'], port=port)


if __name__ == "__main__":
    cli()

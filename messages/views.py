import binascii
import json
from functools import wraps

import requests
from aiohttp import web

from messages.models import Message


def db(fn):
    @wraps(fn)
    async def wrapper(request, *args, **kwargs):
        async with request.app['db'].acquire() as conn:
            request['conn'] = conn
            res = await fn(request, *args, **kwargs)
            await conn.commit()
            return res
    return wrapper


def identity_from_token(header, path):
    resp = requests.get(path, headers={'Authorization': header})
    data = resp.json()
    return data['user_id']


def user_id_from_token(fn):
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        try:
            header = request.headers['Authorization']
            path = request.app['config']['auth']['url']
            user_id = identity_from_token(header, path)
            request['user_id'] = user_id
            return fn(request, *args, **kwargs)
        except (binascii.Error, KeyError):
            raise web.HTTPUnauthorized
    return wrapper


@db
@user_id_from_token
async def index(request):
    sender_id = int(request.match_info['sender_id'])
    messages = await Message.get_by_receiver_and_sender(
        request['conn'], request['user_id'], sender_id)
    if not messages:
        raise web.HTTPNotFound()
    for message in messages:
        message['on'] = message['on'].isoformat()
    return web.json_response({
        'messages': messages
    })


@db
@user_id_from_token
async def post_message(request):
    data = await request.content.read()
    data = json.loads(data)
    data = {'from': request['user_id'], 'to': data['to'], 'message': data['message']}
    await Message.save(request['conn'], data)
    return web.HTTPNoContent()

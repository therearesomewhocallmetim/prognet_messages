from messages.views import index, post_message


def setup_routes(app):
    app.router.add_get('/message/{sender_id:\d+}', index)
    app.router.add_post('/message', post_message)

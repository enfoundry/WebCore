#!/usr/bin/env python

import web.core
from paste import httpserver

class RootController(web.core.Controller):
    def index(self):
        raise web.core.http.HTTPFound(location="/index.html")

app = web.core.Application.factory(root=RootController, debug=False, **{'web.static': True, 'web.static.path': '_html'})
httpserver.serve(app, host='0.0.0.0', port='8000')

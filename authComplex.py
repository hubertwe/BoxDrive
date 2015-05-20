from __future__ import print_function, unicode_literals

import bottle
import os
from threading import Thread, Event
import webbrowser
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler, make_server

from boxsdk import OAuth2


CLIENT_ID = 'l2xl33zviyg2b75tponbcjztason1ppi'  # Insert Box client ID here
CLIENT_SECRET = 'ijzDjgoiMXodVilh6K1CdtRRxbgFfJo6'  # Insert Box client secret here

class O2AuthComplex:
    def __init__(self, config):
        self.config = config

    def authenticate(self):
        class StoppableWSGIServer(bottle.ServerAdapter):
            def __init__(self, *args, **kwargs):
                super(StoppableWSGIServer, self).__init__(*args, **kwargs)
                self._server = None

            def run(self, app):
                server_cls = self.options.get('server_class', WSGIServer)
                handler_cls = self.options.get('handler_class', WSGIRequestHandler)
                self._server = make_server(self.host, self.port, app, server_cls, handler_cls)
                self._server.serve_forever()

            def stop(self):
                self._server.shutdown()

        auth_code = {}
        auth_code_is_available = Event()

        local_oauth_redirect = bottle.Bottle()

        @local_oauth_redirect.get('/')
        def get_token():
            auth_code['auth_code'] = bottle.request.query.code
            auth_code['state'] = bottle.request.query.state
            auth_code_is_available.set()

        local_server = StoppableWSGIServer(host='localhost', port=8080)
        server_thread = Thread(target=lambda: local_oauth_redirect.run(server=local_server))
        server_thread.start()

        oauth = OAuth2(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        auth_url, csrf_token = oauth.get_authorization_url('http://localhost:8080')
        webbrowser.open(auth_url)

        auth_code_is_available.wait()
        local_server.stop()
        assert auth_code['state'] == csrf_token
        access_token, refresh_token = oauth.authenticate(auth_code['auth_code'])

        print("Will use access_token as " + self.config["access_token"])
        print("Will use refresh_token as " + self.config["refresh_token"])
        self.config["access_token"] = access_token
        self.config["refresh_token"] = refresh_token
        return oauth

if __name__ == '__main__':
    authenticate()
    os._exit(0)
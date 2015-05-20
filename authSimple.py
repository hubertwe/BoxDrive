from __future__ import print_function, unicode_literals
from boxsdk import OAuth2

CLIENT_ID = 'l2xl33zviyg2b75tponbcjztason1ppi'
CLIENT_SECRET = 'ijzDjgoiMXodVilh6K1CdtRRxbgFfJo6'

class O2AuthSimple:
    def __init__(self, config):
        self.config = config

    def authenticate(self):
        print("Using simple authentication method.")
        print("Will use access_token as " + self.config["access_token"])
        print("Will use refresh_token as " + self.config["refresh_token"])
        oauth = OAuth2(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            refresh_token=self.config["refresh_token"],
            access_token=self.config["access_token"],
            store_tokens=self.store_tokens)
        return oauth

    def store_tokens(self, access_token, refresh_token):
        self.config["refresh_token"] = refresh_token
        self.config["access_token"] = access_token
        print("Got new access token " + access_token)
        print("Got new refresh " + refresh_token)
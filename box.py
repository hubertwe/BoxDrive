# https://developers.box.com/docs/

from __future__ import print_function, unicode_literals
import os
from boxsdk import Client
from auth import authenticate
import time

class Box(Client):
    def __init__(self):
        self.auth = authenticate()
        self.lastEventStreamPosition = 'now'
        Client.__init__(self, self.auth)

    def getLastEvents(self):
        eventsPack = self.events().get_events(limit=100, stream_position=self.lastEventStreamPosition)
        self.lastEventStreamPosition = eventsPack['next_stream_position']
        return eventsPack['entries']


class Uploader:
    def __init__(self, box):
        pass

class Downloader:
    def __init__(self, box):
        pass

def main():
    box = Box()
    while True:
        for event in box.getLastEvents():
            print(event)
        time.sleep(5)

    os._exit(0)

if __name__ == '__main__': 
    main()

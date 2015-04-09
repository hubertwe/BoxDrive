from __future__ import print_function, unicode_literals
import os
from boxsdk import Client
from auth import authenticate

class Box(Client):
    def __init__(self):
        self.auth = authenticate()
        Client.__init__(self, self.auth)

class Uploader:
    def __init__(self, box):
        pass

class Downloader:
    def __init__(self, box):
        pass

def main():
    box = Box()
    #streamPosition = box.events().get_latest_stream_position()
    #print(streamPosition)
    #options = box.events().get_long_poll_options()
    #while True:
        #print(box.events().long_poll(options=options,stream_position=streamPosition))

    streamPosition = 0

    while True:
        returnInfo = box.events().get_events(limit=1, stream_position=streamPosition)
        streamPosition = returnInfo['next_stream_position']
        print(streamPosition)
        for event in returnInfo['entries']:
            pass #print(event)

    #print(box.events().get_events(limit=2))


    os._exit(0)

if __name__ == '__main__': 
    main()

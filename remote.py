#from __future__ import print_function, unicode_literals
#import os
#from boxsdk import Client
#from auth import authenticate

import threading
import time
from box import Box


class Observer(threading.Thread):

    def __init__(self, box, updateTime = 6):
        super(Observer, self).__init__()
        self.box = box
        self.handler = Handler()
        self.isStopped = False
        self.time = updateTime
        self.ids = set()

    def run(self):
        while(not self.isStopped):
            for event in self.getEvents():
                print event['event_id']
                print event
            time.sleep(self.time)

    def stop(self):
        self.isStopped = True
        self.join()

    def getEvents(self):
        events = box.getLastEvents()
        newEvents =  list()
        ids = set([event['event_id'] for event in events])
        for event in events:
            if event['event_id'] not in self.ids:
                newEvents.append(event)
        self.ids = ids
        return newEvents

    def processEvent(self, event):
        pass


class Event:

    def __init__(self):
        self.is_directory = bool()
        self.src_path = str()
        self.dest_path = str()


class Handler:

    def __init__(self):
        pass

    def on_any_event(self, event):
        pass

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        pass

    def on_moved(self, event):
        pass




'''
def get_events(client):
    print(client.events().get_events(limit=100, stream_position='now'))

def get_latest_stream_position(client):
    print(client.events().get_latest_stream_position())

def run_examples(oauth):
    client = Client(oauth)
    get_events(client)
    get_latest_stream_position(client)

    #routine below should be run on different thread cause it's blocking!
    for event in client.events().generate_events_with_long_polling():
        print('------------------------------------------------')
        print('New notification arrived!')
        print('Event type ' + event.get('event_type',''))
        print('File hash ' + event.get('source').get('sha1',''))
        print('File name ' + event.get('source').get('name',''))
        print('File type ' + event.get('source').get('type',''))

        absolutePath = '';

        for directory in event.get('source').get('path_collection').get('entries'):
            absolutePath = absolutePath +'/'+ directory.get('name')

        print('Path ' + '"' + absolutePath + '"')
        print('All info below:')
        print(event)
        print('------------------------------------------------')
def main():
    oauth = authenticate()
    run_examples(oauth)
    os._exit(0)
'''

if __name__ == '__main__':
    box = Box()
    observer = Observer(box)
    observer.start()
    time.sleep(60)
    #observer.stop()
    '''
    print observer.getEvents([{'event_id' : 1}, {'event_id' : 2}, {'event_id' : 3}])
    print observer.ids
    print observer.getEvents([{'event_id' : 2}, {'event_id' : 3}, {'event_id' : 4}])
    print observer.ids
    '''
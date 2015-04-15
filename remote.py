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

    def processEvent(self, event):
        pass

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
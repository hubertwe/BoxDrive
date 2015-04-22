# https://developers.box.com/docs/

import os
import boxsdk
from auth import authenticate
from path import *


class EventType:
    UNKNOWN = 0
    CREATE = 1
    UPDATE = 2
    DELETE = 3


class Event:

    def __init__(self):
        self.type = EventType.UNKNOWN
        self.is_directory = bool()
        self.path = str()
        self.sha1 = ""
        self.author = str()


class Box(boxsdk.Client):

    def __init__(self):
        self.auth = authenticate()
        self.lastEventStreamPosition = 'now'
        boxsdk.Client.__init__(self, self.auth)

    def getLastEvents(self):
        eventsPack = self.events().get_events(limit=100, stream_position=self.lastEventStreamPosition)
        self.lastEventStreamPosition = eventsPack['next_stream_position']
        events = eventsPack['entries']
        newEvents =  list()
        ids = set([event['event_id'] for event in events])
        for event in events:
            if event['event_id'] not in self.ids:
                newEvents.append(event)
        self.ids = ids
        return self.__convertEvents(newEvents)

    def getItem(self, path):
        path = normalize(path)
        if not path:
            return self.getRoot()
        name = os.path.basename(path)
        if not name:
            return None
        dirPath = os.path.dirname(path)
        if not dirPath or dirPath == '.' or dirPath == '/':
            folders = list()
        else:
            folders = dirPath.split('/')
        current = self.getRoot()
        for folder in folders:
            current = self.getChild(folder, current, 'folder')
            if not current:
                return None
        result = self.getChild(name, current, 'file')
        if result is None:
            return self.getChild(name, current, 'folder')
        else:
            return result

    def getRoot(self):
        return self.folder(folder_id = '0').get()

    def getChild(self, name, parent, type = 'file'):
        if not parent or not name:
            return None
        items = parent.get_items(limit = 1000)
        for item in items:
            if item.name == name and item.type == type:
                return item
        return None

    def __getType(self, boxEvent):
        conversion = {'ITEM_CREATE' : EventType.CREATE,
                      'ITEM_UPLOAD' : EventType.UPDATE,
                      'ITEM_TRASH'  : EventType.DELETE}
        return (conversion.get(boxEvent['event_type'], EventType.UNKNOWN))

    def __getFullPathFromEvent(self, boxEvent):
        source = boxEvent['source']
        entries = source['path_collection']['entries']
        if not entries or entries[0]['name'] == 'Trash':
            parent = self.folder(folder_id = source['parent']['id']).get()
            try:
                entries = parent.path_collection['entries']
                entries.append({'name' : parent.name})
            except KeyError:
                entries = list()
        fullpath = str()
        for entry in entries:
            if(entry['name'] == 'All Files'):
                continue
            fullpath = fullpath + entry['name'] + "/"
        return fullpath + source['name']

    def __convertEvents(self, eventList):
        convertedEvents = list()
        for event in eventList:
            try:
                newEvent = Event()
                newEvent.type = self.__getType(event)
                newEvent.path = self.__getFullPathFromEvent(event)
                newEvent.is_directory = bool(event['source']['type'] == 'folder')
                newEvent.sha1 = event['source'].get('sha1', 0)
                convertedEvents.append(newEvent)
            except (TypeError, KeyError):
                continue
        return convertedEvents


def testBox():
    box = Box()
    root_folder = box.folder(folder_id='0').get()

    items = root_folder.get_items(limit=10, offset=0)
    print('This is the first 10 items in the root folder:')
    for item in items:
        print item
        print("   " + item.name + " : " + item.type)
        itemsDeeper = item.get_items(limit=10)
        for item2 in itemsDeeper:
            print("       " + item2.name + " : " + item2.type)

    # while True:
    #    for event in box.getLastEvents():
    #        print("Type: " + str(event.type))
    #        print("Is directory: " + str(event.is_directory))
    #        print("Sha1: " + str(event.sha1))
    #        print("Path: " + str(event.path))
    # time.sleep(5)

if __name__ == '__main__':
    #testBox()
    box = Box()
    root = box.getRoot()
    file = box.getItem('box')
    new = box.folder(folder_id = file.id).get()
    'NEW'
    print new.name
    print new.id
    print new.path_collection
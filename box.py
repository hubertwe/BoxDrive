# https://developers.box.com/docs/

import os
import boxsdk
from authSimple import O2AuthSimple
from authComplex import O2AuthComplex
from path import *
from event import EventType, Event
from boxsdk.exception import BoxException

class Box(boxsdk.Client):

    def __init__(self, config):
        #self.O2A = O2AuthSimple(config)
        self.auth = O2AuthSimple(config).authenticate()
        self.lastEventStreamPosition = 'now'
        boxsdk.Client.__init__(self, self.auth)
        try:
            self.getRoot()
        except BoxException:
            print("Got oAuthException. Tokens expired. Complex authentication will be done!")
            self.auth = O2AuthComplex(config).authenticate()
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
            if entry['name'] == 'All Files':
                continue
            fullpath = fullpath + entry['name'] + "/"
        return fullpath + source['name']

    def __convertEvents(self, eventList):
        convertedEvents = list()
        for event in eventList:
            try:
                if event['source']['parent'] is None:
                    # This is reported for files inside deleting folder
                    continue
                newEvent = Event(
                    type=self.__getType(event),
                    path=self.__getFullPathFromEvent(event),
                    is_directory=bool(event['source']['type'] == 'folder'),
                    sha1=event['source'].get('sha1', 0),
                    created_by=event['created_by']['id']
                )
                convertedEvents.append(newEvent)
            except (TypeError, KeyError):
                continue
        return convertedEvents

if __name__ == '__main__':
    box = Box(loadConfig('config.cfg'))
    folder = box.getItem('box')
    print folder.get().__dict__
    folder = box.getItem('box/a')
    print folder.get().__dict__

# https://developers.box.com/docs/

from __future__ import print_function, unicode_literals
import os
import boxsdk
from auth import authenticate
import time

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

class Box(boxsdk.Client):
    def __init__(self):
        self.auth = authenticate()
        self.lastEventStreamPosition = 'now'
        boxsdk.Client.__init__(self, self.auth)

    def __getEventType(self, boxEvent):
        conversion = {'ITEM_CREATE' : EventType.CREATE,
                        'ITEM_UPLOAD' : EventType.UPDATE,
                        'ITEM_TRASH' : EventType.DELETE}
        return (conversion.get(boxEvent['event_type'], EventType.UNKNOWN))

    def __getSource(self,boxEvent):
        source = boxEvent.get('source')
        if(source):
            return source
        else:
            raise ValueError('Cant find event source')

    def __getType(self, boxEvent):
        source = self.__getSource(boxEvent)
        typeName = source.get('type')
        if(typeName):
            return typeName
        else:
            raise ValueError('Cant find type name')

    def __getShaFromEvent(self, boxEvent):
        source = self.__getSource(boxEvent)
        sha = source.get('sha1')
        if(sha):
            return sha
        else:
            return 0   #sha is 0 for folders so no throwing exception here

    def __getFullPathFromEvent(self, boxEvent):
        source = self.__getSource(boxEvent)
        filename = source.get('name')
        if(not filename):
            raise ValueError('Cant find name')  
        pathCollection = source.get('path_collection')
        if(not pathCollection):
            raise ValueError('Cant find path_collection') 
        entries = pathCollection.get('entries')
        if(not entries):
            return filename     # specific when trashing file we don't know location
                                # but we know filename and sha1 hash

        fullpath = str()
        for entry in entries:
            name = entry['name']
            if(name == 'All Files'):
                name = '.'
            fullpath = fullpath + name + "/"

        fullpath = fullpath + filename
        return fullpath

    def __convertEvents(self, eventList):
        convertedEvents = list()
        for event in eventList:
            try:
                newEvent = Event()
                newEvent.type = self.__getEventType(event)
                newEvent.is_directory = (self.__getType(event) == 'folder')
                newEvent.sha1 = self.__getShaFromEvent(event) 
                newEvent.path = self.__getFullPathFromEvent(event)
                convertedEvents.append(newEvent)
            except ValueError as e:
                print(e)
        return convertedEvents

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

class Uploader:
    def __init__(self, box):
        self.box = box

    def upload(self, localFileName, remoteFileName):
        rootFolder = self.box.folder(folder_id='0')
        afile = rootFolder.upload(localFileName, file_name=remoteFileName);
        print('File {0} uploaded'.format(afile.get()['name']))

class Downloader:
    def __init__(self, box):
        self.box = box

    def download(self, remoteFileName, localFileName):
        searchResults = self.box.search(
            remoteFileName,
            limit=1,
            offset=0,
            ancestor_folders=[self.box.folder(folder_id='0')])

        for item in searchResults:
            itemWithName = item.get(fields=['name'])
            print('Found matching file {1}-{0} to download'.format(itemWithName.name,itemWithName.id))
            fileToDownload = self.box.file(file_id=itemWithName.id)
            file = open(localFileName, 'w')
            fileToDownload.download_to(file)
            print('Download finished')

def main():
    box = Box()
    while True:
       for event in box.getLastEvents():
           print("Type: " + str(event.type))
           print("Is directory: " + str(event.is_directory))
           print("Sha1: " + str(event.sha1))
           print("Path: " + str(event.path))
    time.sleep(5)

    # up = Uploader(box)
    # down  = Downloader(box)

    # try:
    #     up.upload('README.md', 'README.md_uploaded')
    # except boxsdk.exception.BoxAPIException as e:
    #     print("File You're trying to upload already exists remotely")
    #     print(e)

    # down.download('README.md_uploaded', 'README.md_downloaded')

    os._exit(0)

if __name__ == '__main__': 
    main()

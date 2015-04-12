# https://developers.box.com/docs/

from __future__ import print_function, unicode_literals
import os
import boxsdk
from auth import authenticate
import time

class Box(boxsdk.Client):
    def __init__(self):
        self.auth = authenticate()
        self.lastEventStreamPosition = 'now'
        boxsdk.Client.__init__(self, self.auth)

    def getLastEvents(self):
        eventsPack = self.events().get_events(limit=100, stream_position=self.lastEventStreamPosition)
        self.lastEventStreamPosition = eventsPack['next_stream_position']
        return eventsPack['entries']


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
            ancestor_folders=[self.box.folder(folder_id='0')]
        )

        for item in searchResults:
            itemWithName = item.get(fields=['name'])
            print('Found matching file {1}-{0} to download'.format(itemWithName.name,itemWithName.id))
            fileToDownload = self.box.file(file_id=itemWithName.id)
            file = open(localFileName, 'w')
            fileToDownload.download_to(file)
            print('Download finished')

def main():
    box = Box()
    # while True:
    #     for event in box.getLastEvents():
    #         print(event)
    #     time.sleep(5)

    up = Uploader(box)
    down  = Downloader(box)

    try:
        up.upload('README.md', 'README.md_uploaded')
    except boxsdk.exception.BoxAPIException as e:
        print("File You're trying to upload already exists remotely")
        print(e)

    down.download('README.md_uploaded', 'README.md_downloaded')

    os._exit(0)

if __name__ == '__main__': 
    main()

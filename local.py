import shutil
from watchdog.observers import Observer as FileSystemObserver
from watchdog.events import FileSystemEventHandler
from box import Box
from path import *
from event import Event, EventType
from helper import sha1

from Crypto.Cipher import AES
import io
import struct

SOME_KEY = "0123456789ABCDEF"
SOME_IV  = "0123456789ABCDEF"

'''
    Observes local file system changes in new thread.
    (see watchdog.observers.Observer for more details)

    Calls Handler methods on files events
'''
class Observer():

    def __init__(self, path, handler):
        self.observer = FileSystemObserver()
        self.path = path
        self.handler = handler

    def start(self):
        self.observer.schedule(self.handler, self.path, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


class Handler(FileSystemEventHandler):

    def __init__(self, updater, eventList):
        super(Handler, self).__init__()
        self.updater = updater
        self.events = eventList

    def dispatch(self, event):
        event = Event.fromLocalEvent(event)
        if not self.__isUpdateNeeded(event):
            return
        if event.type == EventType.CREATE:
            self.on_created(event)
        elif event.type == EventType.UPDATE:
            self.on_modified(event)
        elif event.type == EventType.DELETE:
            self.on_deleted(event)
        elif event.type == EventType.MOVED:
            self.on_moved(event)

    def on_created(self, event):
        print 'local/event | create: ' + event.path
        if event.is_directory:
            self.updater.createDir(event.path)
        else:
            self.updater.createFile(event.path)

    def on_deleted(self, event):
        print 'local/event | delete: ' + event.path
        self.updater.delete(event.path)

    def on_modified(self, event):
        if event.is_directory:
            return
        print 'local/event | modify: ' + event.path
        self.updater.update(event.path)

    def on_moved(self, event):
        print 'local/event | moved: ' + event.path + ' -> ' + event.dest_path
        self.updater.delete(event.path)
        if event.is_directory:
            self.updater.createDir(event.dest_path)
        else:
            self.updater.createFile(event.dest_path)

    def __isUpdateNeeded(self, event):
        if event.is_directory and event.type == EventType.UPDATE:
            return False
        eventFromList = self.events.get(event)
        if eventFromList:
            self.events.remove(eventFromList)
            return False
        return True

def decrypt_file(inBuffer, filename, chunksize=64*1024):
    decryptor = AES.new(SOME_KEY, AES.MODE_CBC, SOME_IV)
    origsize = struct.unpack('<Q', inBuffer.read(struct.calcsize('Q')))[0]
    with open(filename, 'wb') as outfile:
        while True:
            chunk = inBuffer.read(chunksize)
            if len(chunk) == 0:
                break
            outfile.write(decryptor.decrypt(chunk))
        outfile.truncate(origsize)

class Updater:

    def __init__(self, path, box):
        self.box = box
        self.path = normalize(path)

    def createFile(self, path):
        absolutePath = absolute(self.path, path)
        print 'local/update | Creating new file... ' + absolutePath
        if os.path.exists(absolutePath):
            print 'local/update | Nothing to create, file already exists:  ' + absolutePath
            return
        dirPath= os.path.dirname(absolutePath)
        file = self.box.getItem(path)
        if file is None:
            print 'local/update | Cant locate file on Box drive: ' + absolutePath
            return
        if not os.path.exists(dirPath):
            print 'local/update | Parent dir doesnt exists: ' + dirPath
            self.createDir(dirPath)
        #stream = open(absolutePath, 'w+')
        output = io.BytesIO()
        file.download_to(output)
        output.seek(0)
        decrypt_file(output, absolutePath)
        print 'local/update | File creation succeeded: ' + absolutePath

    def createDir(self, path):
        absolutePath = absolute(self.path, path)
        print 'local/update | Creating new directory and all parents... ' + absolutePath
        try:
            os.makedirs(absolutePath)
            print 'local/update | Directory creation succeeded: ' + absolutePath
        except OSError: # dir already exists
            print 'local/update | Nothing to create, dir already exists: ' + absolutePath

    def deleteFile(self, path):
        absolutePath = absolute(self.path, path)
        print 'local/update | Deleting file... ' + absolutePath
        if os.path.exists(absolutePath):
            try:
                os.remove(absolutePath)
                print 'local/update | File deletion succeeded: ' + absolutePath
            except OSError: # file is opened by other process
                print 'local/update | Cant delete file, file is opened by another process: ' + absolutePath
        else:
            print 'local/update | Path doesnt exist on local drive: ' + absolutePath

    def deleteDir(self, path):
        absolutePath = absolute(self.path, path)
        print 'local/update | Deleting directory... ' + absolutePath
        if os.path.exists(absolutePath):
            try:
                shutil.rmtree(absolutePath)
                print 'local/update | Dir deletion succeeded: ' + absolutePath
            except OSError: # file is opened by other process
                print 'local/update | Cant delete dir, some files are opened by another process: ' + absolutePath
        else:
            print 'local/update | Path doesnt exist on local drive: ' + absolutePath

    def updateFile(self, path):
        absolutePath = absolute(self.path, path)
        if not os.path.exists(absolutePath):
            self.createFile(path)
            return
        print 'local/update | Updating file... ' + absolutePath
        file = self.box.getItem(path)
        if file is None:
            print 'local/update | Cant locate file on Box drive: ' + absolutePath
            return
        if file.sha1 == sha1(absolutePath):
            print 'local/update | File already up to date: ' + absolutePath
            return
        try:
            stream = open(absolutePath, 'w')
            file.download_to(stream)
            print 'local/update | File updating succeeded: ' + absolutePath
        except IOError:
            print 'local/update | Can\'t open local file: ' + absolutePath


if __name__ == '__main__':
    box = Box()
    updater = Updater('E:/szkola/BoxDrive/', box)
    updater.createFile('./test/a.gdoc')
    updater.createFile('./test/box2/a.txt')
    updater.updateFile('./test/box2/a.txt')

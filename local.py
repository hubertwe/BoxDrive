import os
import shutil
from watchdog.observers import Observer as FileSystemObserver
from watchdog.events import FileSystemEventHandler
from box import Box
from path import *
import hashlib

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

    def __init__(self, updater):
        super(Handler, self).__init__()
        self.updater = updater

    def on_any_event(self, event):
        pass

    def on_created(self, event):
        srcPath = normalize(event.src_path)
        print 'local/event | create: ' + srcPath
        if event.is_directory:
            self.updater.createDir(srcPath)
        else:
            self.updater.createFile(srcPath)

    def on_deleted(self, event):
        srcPath = normalize(event.src_path)
        print 'local/event | delete: ' + srcPath
        self.updater.delete(srcPath)

    def on_modified(self, event):
        srcPath = normalize(event.src_path)
        if not event.is_directory:
            print 'local/event | modify: ' + srcPath
            self.updater.update(srcPath)

    def on_moved(self, event):
        srcPath = normalize(event.src_path)
        destPath = normalize(event.dest_path)
        print 'local/event | moved: ' + srcPath + ' -> ' + destPath
        self.updater.delete(srcPath)
        if event.is_directory:
            self.updater.createDir(destPath)
        else:
            self.updater.createFile(destPath)

def sha1(path):
    hasher = hashlib.sha1()
    try:
        stream = open(path, 'rb')
        hasher.update(stream.read())
        stream.close()
    except IOError:
        return 0
    return hasher.hexdigest()

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
        stream = open(absolutePath, 'w+')
        file.download_to(stream)
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

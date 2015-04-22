import threading
import time
import os
from box import Box, Event, EventType
from boxsdk.exception import BoxAPIException
from path import *


class Observer(threading.Thread):

    def __init__(self, box, handler, updateTime = 6):
        super(Observer, self).__init__()
        self.box = box
        self.handler = handler
        self.isStopped = False
        self.time = updateTime

    def run(self):
        while(not self.isStopped):
            for event in self.box.getLastEvents():
                self.handler.processEvent(event)
            time.sleep(self.time)

    def stop(self):
        self.isStopped = True
        self.join()


class Handler():

    def __init__(self, updater):
        self.updater = updater

    def processEvent(self, event):
        if event.type == EventType.CREATE:
            self.on_created(event)
        elif event.type == EventType.UPDATE:
            self.on_modified(event)
        elif event.type == EventType.DELETE:
            self.on_deleted(event)

    def on_created(self, event):
        srcPath = normalize(event.path)
        print 'remote/event | create: ' + srcPath
        if event.is_directory:
            self.updater.createDir(srcPath)
        else:
            self.updater.createFile(srcPath)

    def on_deleted(self, event):
        srcPath = normalize(event.path)
        print 'remote/event | delete: ' + srcPath
        if event.is_directory:
            self.updater.deleteDir(srcPath)
        else:
            self.updater.deleteFile(srcPath)

    def on_modified(self, event):
        srcPath = normalize(event.path)
        if not event.is_directory:
            print 'remote/event | modify: ' + srcPath
            self.updater.updateFile(srcPath)

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
        self.path = normalize(path)
        self.box = box

    def createFile(self, path):
        relativePath = relative(self.path, path)
        print 'remote/update | Creating new file... ' + relativePath
        file = self.box.getItem(relativePath)
        if file is not None:
            print 'remote/update | File already exists on Box: ' + relativePath
            return
        fileName = os.path.basename(relativePath)
        dirPath = os.path.dirname(relativePath)
        dir = self.box.getItem(dirPath)
        if dir is None:
            print 'remote/update | Parent dir doesnt exists: ' + dirPath
            dir = self.createDir(dirPath)
        dir.upload(path, fileName)
        print 'remote/update | File creation succeeded: ' + relativePath

    def createDir(self, path):
        relativePath = relative(self.path, path)
        print 'remote/update | Creating new directory and all parents... ' + relativePath
        folders = relativePath.split('/')
        current = self.box.getRoot()
        for folder in folders:
            if not folder:
                continue
            next = self.box.getChild(folder, current, 'folder')
            if next is None:
                current = current.create_subfolder(folder)
            else:
                current = next
        print 'remote/update | Directory creation succeeded: ' + relativePath
        return current

    def delete(self, path):
        relativePath = relative(self.path, path)
        print 'remote/update | Deleting item... ' + relativePath
        item = self.box.getItem(relativePath)
        if item is None:
           print 'remote/update | Path doesnt exist on Box drive: ' + relativePath
           return
        item.delete()
        print 'remote/update | Item deletion succeeded: ' + relativePath

    def update(self, path):
        relativePath = relative(self.path, path)
        print 'remote/update | Updating file... ' + relativePath
        file = self.box.getItem(relativePath)
        if file is None:
            print 'remote/update | Cant locate file on Box drive: ' + relativePath
            self.createFile(relativePath)
            return
        if file.sha1 == sha1(path):
            print 'remote/update | File already up to date: ' + relativePath
            return
        file.update_contents(path)
        print 'local/update | File updating succeeded: ' + relativePath

if __name__ == '__main__':
    box = Box()
    u = Updater(box, 'E:/szkola/BoxDrive/')
    u.updateFile('E:/szkola/BoxDrive/test/box/api/a.txt')
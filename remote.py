import threading
import time
import os
from box import Box, Event, EventType
from boxsdk.exception import BoxAPIException


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
        print 'OnCreated ' + event.path
        if event.is_directory:
            self.updater.createDir(event.path)
        else:
            self.updater.createFile(event.path)

    def on_deleted(self, event):
        print 'OnDeleted ' + event.path
        if event.is_directory:
            self.updater.deleteDir(event.path)
        else:
            self.updater.deleteFile(event.path)

    def on_modified(self, event):
        print 'OnModified ' + event.path
        if event.is_directory:
            self.updater.updateFile(event.path)


class Updater:

    def __init__(self, path, box):
        self.path = os.path.normpath(path)
        self.box = box

    def getRelativePath(self, path):
        if self.path in os.path.normpath(path):
            return os.path.normpath(path).split(self.path)[1][1:]
        else:
            return path

    def createFile(self, path):
        relativePath = self.getRelativePath(path)
        fileName = os.path.basename(relativePath)
        dirPath = os.path.dirname(relativePath)
        dir = self.createDir(dirPath)
        dir.upload(path, fileName)

    def createDir(self, path):
        relativePath = self.getRelativePath(path)
        folders = relativePath.split(os.sep)
        current = self.box.getRoot()
        for folder in folders:
            if not folder:
                continue
            try:
                current = current.create_subfolder(folder)
            except BoxAPIException:
                current = self.box.getItem(folder, current)
        return current

    def deleteFile(self, path):
        relativePath = self.getRelativePath(path)
        print 'RELATIVE: ' + relativePath
        file = self.box.getFile(relativePath)
        print file
        if file is not None:
            file.delete()

    def deleteDir(self, path):
        relativePath = self.getRelativePath(path)
        dir = self.box.getDir(relativePath)
        if dir is not None:
            dir.delete()

    def updateFile(self, path):
        relativePath = self.getRelativePath(path)
        file = self.box.getFile(relativePath)
        if file is not None:
            file.update_contents(path)
        else:
            self.createFile(relativePath)

if __name__ == '__main__':
    #box = Box()
    #u = Updater(box, 'E:/szkola/BoxDrive/')
    #u.updateFile('E:/szkola/BoxDrive/test/box/api/a.txt')
    print os.path.basename('sd.txt')
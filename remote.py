import threading
import time
import os
from box import Box
from boxsdk.exception import BoxAPIException


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


class Updater:

    def __init__(self, box, path):
        self.path = os.path.normpath(path)
        self.box = box

    def getRelativePath(self, path):
        if self.path in path:
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
        file = self.box.getFile(relativePath)
        if file is not None:
            file.delete()

    def deleteDir(self, path):
        relativePath = self.getRelativePath(path)
        dir = self.box.getDir(relativePath)
        if dir is not None:
            dir.delete()

    def updateFile(self, path):
        self.deleteFile(path)
        self.createFile(path)

if __name__ == '__main__':
    box = Box()
    u = Updater(box, 'E:/szkola/BoxDrive/')
    u.updateFile('E:/szkola/BoxDrive/test/box/api/a.txt')
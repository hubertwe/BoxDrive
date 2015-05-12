import threading
import time
import os
import hashlib
from box import Box
from boxsdk.exception import BoxAPIException
from path import *
from event import EventType, Event, EventList
import copy


class Observer(threading.Thread):

    def __init__(self, handler, box, updateTime = 6):
        super(Observer, self).__init__()
        self.box = box
        self.handler = handler
        self.isStopped = False
        self.time = updateTime

    def run(self):
        while not self.isStopped:
            for event in self.box.getLastEvents():
                self.handler.dispatch(event)
            time.sleep(self.time)

    def stop(self):
        self.isStopped = True
        self.join()


class Handler():

    def __init__(self, updater, box, eventList):
        self.updater = updater
        self.box = box
        self.events = eventList

    def dispatch(self, event):
        if not self.__isUpdateNeeded(event):
            return
        # TODO: Some ugly hack, please fix me
        eventToAppend = copy.deepcopy(event)
        eventToAppend.path = absolute(self.updater.path, eventToAppend.path)
        self.events.append(eventToAppend)
        # ------
        if event.type == EventType.CREATE:
            self.on_created(event)
        elif event.type == EventType.UPDATE:
            self.on_modified(event)
        elif event.type == EventType.DELETE:
            self.on_deleted(event)

    def on_created(self, event):
        print 'remote/event | create: ' + event.path
        if event.is_directory:
            self.updater.createDir(event.path)
        else:
            self.updater.createFile(event.path)

    def on_deleted(self, event):
        print 'remote/event | delete: ' + event.path
        if event.is_directory:
            self.updater.deleteDir(event.path)
        else:
            self.updater.deleteFile(event.path)

    def on_modified(self, event):
        if not event.is_directory:
            print 'remote/event | modify: ' + event.path
            self.updater.updateFile(event.path)

    def __isUpdateNeeded(self, event):
        if event.created_by == self.box.user().get()['id']:
            return False
        return True


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
        try:
            dir.upload(path, fileName)
        except IOError:
            print 'remote/update | Cant find local file: ' + relativePath
            return
        print 'remote/update | File creation succeeded: ' + relativePath

    def createDir(self, path):
        relativePath = relative(self.path, path)
        print 'remote/update | Creating new directory and all parents... ' + relativePath
        dir = self.box.getItem(relativePath)
        if dir is not None:
            print 'remote/update | Dir already exists on Box: ' + relativePath
            return
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
        try:
            file.update_contents(path)
        except IOError as e:
            print e.errno
            print e
            print 'remote/update | Cant find local file or is blocked: ' + relativePath
            return
        print 'remote/update | File updating succeeded: ' + relativePath

if __name__ == '__main__':
    box = Box()
    u = Updater(box, 'E:/szkola/BoxDrive/')
    u.updateFile('E:/szkola/BoxDrive/test/box/api/a.txt')
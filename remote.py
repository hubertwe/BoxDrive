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

    def __init__(self, box):
        self.box = box

    def createFile(self, path):
        self.box.getRoot().upload(path)

    def createDir(self, path):
        tail, head = os.path.split(path)
        print 'CALL: ' + str(head) + ' | ' + str(tail)
        if not tail:
            print 'tail'
            try:
                current = box.getRoot()
                current.create_subfolder(head)
            except BoxAPIException:
                pass
            return
        print 'CALL: ' + str(head) + ' | ' + str(tail)
        self.createDir(tail)
        print tail
        current = box.getItem(tail)
        print current
        try:
            current.create_subfolder(head)
        except BoxAPIException:
            pass

'''
        'test/box/api'
        'test/box' , 'api'
        'test' ,'box'
        '', 'test'
        folders = os.path.normpath(path).split(os.sep)
        current = self.box.getRoot()
        for folder in folders:
            if not folder:
                continue
            try:
                current = current.create_subfolder(folder)
            except BoxAPIException:
                current = self.box.getItem()
'''

if __name__ == '__main__':
    box = Box()
    item = box.getItem('test/box/')
    print item
    #u = Updater(box)
    #u.createDir('test/box/api')
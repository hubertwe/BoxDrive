from watchdog.observers import Observer as FileSystemObserver
from watchdog.events import FileSystemEventHandler
from box import Box
import os
import shutil

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
        super(Handler, self).on_any_event(event)

    def on_created(self, event):
        super(Handler, self).on_created(event)
        print 'OnCreated ' + event.src_path

    def on_deleted(self, event):
        super(Handler, self).on_deleted(event)
        print 'OnDeleted ' + event.src_path

    def on_modified(self, event):
        super(Handler, self).on_modified(event)
        print 'OnModified ' + event.src_path

    def on_moved(self, event):
        super(Handler, self).on_moved(event)
        print 'OnMoved ' + event.src_path + ' | ' + event.dest_path


class Updater:

    def __init__(self, path, box):
        self.box = box
        self.path = path

    def createFile(self, path):
        file = self.box.getItem(path)
        if not file:
            return
        path = os.path.join(self.path, path)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        stream = open(path, 'w+')
        file.download_to(stream)

    def createDir(self, path):
        try:
            os.mkdir(path)
        except OSError: # dir already exists
            pass

    def deleteFile(self, path):
        path = os.path.join(self.path, path)
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError: # file is opened by other process
                pass

    def deleteDir(self, path):
        path = os.path.join(self.path, path)
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except OSError: # file is opened by other process
                pass

    def updateFile(self, path):
        file = self.box.getItem(path)
        path = os.path.join(self.path, path)
        if os.path.exists(path):
            self.deleteFile(path)
        self.createFile(path)

if __name__ == '__main__':
    box = Box()
    updater = Updater('E:/szkola/BoxDrive/', box)
    updater.createFile('test/as/b.txt')
    #print os.path.join('E:/szkola/BoxDrive', 'E:/szkola/BoxDrive/test/as/b.txt')

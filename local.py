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
        if event.is_directory:
            self.updater.createDir(event.src_path)
        else:
            self.updater.createFile(event.src_path)

    def on_deleted(self, event):
        super(Handler, self).on_deleted(event)
        print 'OnDeleted ' + event.src_path
        if event.is_directory:
            self.updater.deleteDir(event.src_path)
        else:
            self.updater.deletFile(event.src_path)

    def on_modified(self, event):
        super(Handler, self).on_modified(event)
        print 'OnModified ' + event.src_path
        if event.is_directory:
            self.updater.updateFile(event.src_path)

    def on_moved(self, event):
        super(Handler, self).on_moved(event)
        print 'OnMoved ' + event.src_path + ' | ' + event.dest_path
        if event.is_directory:
            self.updater.deleteDir(event.src_path)
            self.updater.createDir(event.dest_path)
        else:
            self.updater.deletFile(event.src_path)
            self.updater.createFile(event.dest_path)


class Updater:

    def __init__(self, path, box):
        self.box = box
        self.path = path

    def getAbsolutePath(self, path):
        return os.path.join(self.path, path)

    def createFile(self, path):
        absolutePath = self.getAbsolutePath(path)
        if os.path.exists(absolutePath):
            return
        dirPath= os.path.dirname(absolutePath)
        file = self.box.getFile(path)
        if file is None:
            return
        if not os.path.exists(dirPath):
            self.createDir(dirPath)
        stream = open(absolutePath, 'w+')
        file.download_to(stream)

    def createDir(self, path):
        absolutePath = self.getAbsolutePath(path)
        try:
            os.makedirs(absolutePath)
        except OSError: # dir already exists
            pass

    def deleteFile(self, path):
        absolutePath = self.getAbsolutePath(path)
        if os.path.exists(absolutePath):
            try:
                os.remove(absolutePath)
            except OSError: # file is opened by other process
                pass

    def deleteDir(self, path):
        absolutePath = self.getAbsolutePath(path)
        if os.path.exists(absolutePath):
            try:
                shutil.rmtree(absolutePath)
            except OSError: # file is opened by other process
                pass

    def updateFile(self, path):
        absolutePath = self.getAbsolutePath(path)
        file = self.box.getFile(path)
        if file is None:
            return
        stream = open(absolutePath, 'w')
        file.download_to(stream)

if __name__ == '__main__':
    box = Box()
    updater = Updater('E:/szkola/BoxDrive/', box)
    updater.createFile('./test/a.gdoc')
    updater.createFile('./test/box2/a.txt')
    updater.updateFile('./test/box2/a.txt')

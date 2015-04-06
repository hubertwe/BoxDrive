from watchdog.observers import Observer as FileSystemObserver
from watchdog.events import FileSystemEventHandler

'''
    Observes local file system changes in new thread.
    (see watchdog.observers.Observer for more details)

    Calls Handler methods on files events
'''
class Observer():

    def __init__(self, path):
        self.observer = FileSystemObserver()
        self.path = path
        self.handler = Handler()

    def start(self):
        self.observer.schedule(self.handler, self.path, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


class Handler(FileSystemEventHandler):

    def __init__(self):
        super(Handler, self).__init__()

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
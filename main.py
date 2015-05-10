import local
import remote
from box import Box
import time
import argparse
from event import EventList

ROOT_FOLDER = 'Some:/path/here'

def startRemote(path, box, eventList):
    updater = local.Updater(path, box)
    handler = remote.Handler(updater, box, eventList)
    observer = remote.Observer(handler, box)
    observer.start()
    return observer

def startLocal(path, box, eventList):
    updater = remote.Updater(path, box)
    handler = local.Handler(updater, eventList)
    observer = local.Observer(path, handler)
    observer.start()
    return observer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', nargs=1, required=True,
                        type=str, dest='root_folder',
                        help='Local path which should be synchronized with Box root')
    path = parser.parse_args().root_folder[0]
    print path
    box = Box()
    eventList = EventList()
    remoteObserver = startRemote(path, box, eventList)
    localObserver = startLocal(path, box, eventList)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print 'Stopping observers, please wait!'
            remoteObserver.stop()
            localObserver.stop()
            print 'Bye, bye!'
            break
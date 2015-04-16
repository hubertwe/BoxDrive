import local
import remote
from box import Box


def startRemote(path, box):
    updater = local.Updater(path, box)
    handler = remote.Handler(updater)
    observer = remote.Observer(box, handler)
    observer.start()

def startLocal(path, box):
    updater = remote.Updater(path, box)
    handler = local.Handler(updater)
    observer = local.Observer(path, handler)
    observer.start()

if __name__ == "__main__":
    path = 'E:/szkola/drive'
    box = Box()
    startRemote(path, box)
    startLocal(path, box)
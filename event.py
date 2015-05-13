import threading
from path import normalize
from helper import sha1


class EventType:
    UNKNOWN = 'unknown'
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    MOVED = 'moved'

    @classmethod
    def fromLocalType(cls, localType):
        if localType == 'moved':
            return cls.MOVED
        elif localType == 'deleted':
            return cls.DELETE
        elif localType == 'created':
            return cls.CREATE
        elif localType == 'modified':
            return cls.UPDATE


class Event:

    def __init__(self, path='', dest_path='', type=EventType.UNKNOWN,
                 is_directory=False, sha1='', created_by=''):
        self.type = type
        self.is_directory = is_directory
        self.path = normalize(path)
        self.dest_path = normalize(dest_path)
        self.sha1 = sha1
        self.created_by = created_by

    def __eq__(self, other):
        return bool(self.path == other.path and self.type == other.type)

    def __repr__(self):
        return str({'type': self.type, 'path': self.path})

    @classmethod
    def fromLocalEvent(cls, localEvent):
        srcPath = normalize(localEvent.src_path)
        try:
            destPath = normalize(localEvent.dest_path)
        except AttributeError:
            destPath = ''
        return cls(
            path=srcPath,
            dest_path=destPath,
            type=EventType.fromLocalType(localEvent.event_type),
            is_directory=localEvent.is_directory,
            sha1=sha1(srcPath)
        )


class EventList:

    def __init__(self):
        self.events = list()
        self.lock = threading.Lock()

    def __repr__(self):
        return str(self.events)

    def append(self, event):
        self.lock.acquire()
        self.events.append(event)
        self.lock.release()

    def get(self, event):
        self.lock.acquire()
        for currentEvent in self.events:
            if currentEvent == event:
                self.lock.release()
                return currentEvent
        self.lock.release()
        return None

    def remove(self, event):
        self.lock.acquire()
        index = self.events.index(event)
        self.events = self.events[index + 1:]
        self.lock.release()


if __name__ == '__main__':
    events = EventList()
    ev1 = Event(path='aaa', type=EventType.CREATE)
    ev2 = Event(path='bbb', type=EventType.fromLocalType('deleted'))
    ev3 = Event(path='C:/a/bbb', type=EventType.DELETE)
    events.append(ev1)
    events.append(ev2)
    print events.events
    toRemove = events.get(ev3)
    events.remove(toRemove)
    print events.events
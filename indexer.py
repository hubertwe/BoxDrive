import os
import boxsdk
from box import Box
import hashlib
from glob import glob

class Indexer:
    
    def __init__(self):
        pass

    def __sha(self, path):
        hasher = hashlib.sha1()
        try:
            stream = open(path, 'rb')
            hasher.update(stream.read())
            stream.close()
        except IOError:
            return 0
        return hasher.hexdigest()

    def local(self, directoryPath):
        result = dict()
        for root, dirnames, filenames in os.walk(directoryPath):
            for filename in filenames:
                fullFilename = os.path.join(root,filename) 
                result[fullFilename] = self.__sha(fullFilename)
        
        for key, element in result.items():
            print(str(element) + " - " + str(key))
        pass

    def __processDirectory(self, directoryObject):
        items = directoryObject.get_items(limit=1000)
        for item in items:
            print(item)
            if type(item) is boxsdk.object.folder.Folder:
                print("Running resursively")
                self.__processDirectory(item)

    def remote(self, box, directoryPath):
        root = box.getRoot()
        items = root.get_items(limit = 1000)
        for fileObject in items:
            print(fileObject)


if __name__ == '__main__':
    index = Indexer();
    index.local('.');
    box = Box();
    index.remote(box,'any')
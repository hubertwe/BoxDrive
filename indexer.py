import os
import boxsdk
from box import Box
import hashlib
from glob import glob

class FileIndex():
    def __init__(self, filename, path, sha1):
        self.filename = filename
        self.path = path
        self.sha1 = sha1
    def getName(self):
        return self.filename

    def getPath(self):
        return self.path

    def getSha(self):
        return self.sha1

class Indexer:
    
    def __init__(self):
        self.remoteFiles = list()
        self.localFiles = list()

    def getRemoteIndex(self):
        return self.remoteFiles

    def getLocalIndex(self):
        return self.localFiles

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
        print("Local indexing started...")
        for root, dirnames, filenames in os.walk(directoryPath):
            for filename in filenames:
                fullFilename = os.path.join(root,filename) 
                self.localFiles.append(FileIndex(filename, root, self.__sha(fullFilename)))
        print("Local indexing finished.")

    def __processDirectory(self, directoryObject):
        items = directoryObject.get_items(limit=10000)
        currentPath = "";
        for item in items:
            if type(item) is boxsdk.object.folder.Folder:
                self.__processDirectory(item)
            else:
                fileInfo = item.get()  
                for element in fileInfo['path_collection']['entries']:
                    if element['id'] == '0':
                        element['name'] = '.'
                    currentPath += element['name'] + '/'
                self.remoteFiles.append(FileIndex(fileInfo['name'],currentPath,fileInfo['sha1']))

    def remote(self, box):
        print("Remote indexing started...")
        root = box.getRoot()
        self.__processDirectory(root)
        print("Remote indexing finished.")

if __name__ == '__main__':
    index = Indexer();
    index.local('.');
    box = Box();
    index.remote(box);
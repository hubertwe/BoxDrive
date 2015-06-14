import os
import boxsdk
from box import Box
import hashlib
from local import Updater
from path import normalize
import shutil

class FileIndex():

    def __init__(self, filename, path, sha1, isDir=False):
        self.filename = filename
        self.path = path
        self.sha1 = sha1
        self.isDir = isDir


class Indexer:
    
    def __init__(self, path, box):
        self.box = box
        self.path = normalize(path)
        self.updater = Updater(path, box)
        self.remoteFiles = list()
        self.localFiles = list()

    def synchronize(self):
        self.__clearDir(self.path)
        self.remote(self.box)
        for file in self.remoteFiles:
            path = os.path.join(file.path, file.filename)
            print 'INDEXER: ' + path
            if file.isDir:
                self.updater.createDir(path)
            else:
                self.updater.updateFile(path)

    def getRemoteIndex(self):
        return self.remoteFiles

    def getLocalIndex(self):
        return self.localFiles

    def __clearDir(self, path):
        for item in os.listdir(path):
            currentPath = os.path.join(path, item)
            try:
                if os.path.isdir(currentPath):
                    shutil.rmtree(currentPath)
                else:
                    os.remove(currentPath)
            except OSError:
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
        print("Local indexing started...")
        for root, dirnames, filenames in os.walk(directoryPath):
            for filename in filenames:
                fullFilename = os.path.join(root,filename) 
                self.localFiles.append(FileIndex(filename, root, self.__sha(fullFilename)))
        print("Local indexing finished.")

    def __processDirectory(self, directoryObject):
        items = directoryObject.get_items(limit=10000)
        for item in items:
            currentPath = '';
            fileInfo = item.get()
            for element in fileInfo['path_collection']['entries']:
                if element['id'] == '0':
                    continue
                currentPath += element['name'] + '/'
            if type(item) is boxsdk.object.folder.Folder:
                self.remoteFiles.append(FileIndex(fileInfo['name'], currentPath, '', True))
                self.__processDirectory(item)
            else:
                self.remoteFiles.append(FileIndex(fileInfo['name'], currentPath, fileInfo['sha1']))

    def remote(self, box):
        print("Remote indexing started...")
        root = box.getRoot()
        self.__processDirectory(root)
        print("Remote indexing finished.")

if __name__ == '__main__':
    path = ('E:\pwr\BoxDrive\\test')

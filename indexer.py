import os
import boxsdk
from box import Box
import hashlib
from local import Updater as LocalUpdater
from remote import Updater as RemoteUpdater
from path import normalize, relative, absolute
import shutil
from helper import sha1, encrypt
import io

class FileIndex():

    def __init__(self, filename, path, sha1, isDir=False):
        self.filename = filename
        self.path = path
        self.sha1 = sha1
        self.isDir = isDir
        self.wasIndexed = False


class Indexer:
    
    def __init__(self, path, key, box):
        self.box = box
        self.key = key
        self.path = normalize(path)
        self.localUpdater = LocalUpdater(path, key, box)
        self.remoteUpdater = RemoteUpdater(path, key, box)
        self.remoteFiles = list()
        self.localFiles = list()
        self.localDirs = list()
        self.remoteDirs = list()

    def synchronize(self):
        self.remote(self.box)
        self.local(self.path)
        print 'Synchronization started...'
        for remote in self.remoteDirs:
            remotePath = os.path.join(remote.path, remote.filename)
            for local in self.localDirs:
                localPath = relative(self.path, os.path.join(local.path, local.filename))
                if remotePath == localPath:
                    local.wasIndexed = True
                    remote.wasIndexed = True
                    break
            if not remote.wasIndexed:
                self.localUpdater.createDir(remotePath)

        for remote in self.remoteFiles:
            remotePath = os.path.join(remote.path, remote.filename)
            for local in self.localFiles:
                localPath = relative(self.path, os.path.join(local.path, local.filename))
                if remotePath == localPath:
                    if remote.sha1 != local.sha1:
                        self.localUpdater.updateFile(remotePath)
                    local.wasIndexed = True
                    remote.wasIndexed = True
                    break
            if not remote.wasIndexed:
                self.localUpdater.createFile(remotePath)

        for local in self.localDirs:
            if not local.wasIndexed:
                localPath = os.path.join(local.path, local.filename)
                self.remoteUpdater.createDir(localPath)

        for local in self.localFiles:
            if not local.wasIndexed:
                localPath = os.path.join(local.path, local.filename)
                self.remoteUpdater.createFile(localPath)
    print 'Synchronization finished.'

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
            for filename in filenames + dirnames:
                fullFilename = os.path.join(root,filename)
                if os.path.isdir(fullFilename):
                    self.localDirs.append(FileIndex(filename, normalize(root), '', True))
                else:
                    output = io.BytesIO()
                    encrypt(fullFilename, output, self.key)
                    self.localFiles.append(FileIndex(filename, normalize(root), sha1(output)))
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
                self.remoteDirs.append(FileIndex(fileInfo['name'], currentPath, '', True))
                self.__processDirectory(item)
            else:
                self.remoteFiles.append(FileIndex(fileInfo['name'], currentPath, fileInfo['sha1']))

    def remote(self, box):
        print("Remote indexing started...")
        root = box.getRoot()
        self.__processDirectory(root)
        print("Remote indexing finished.")

if __name__ == '__main__':
    pass
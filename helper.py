import hashlib
from Crypto.Cipher import AES
import struct
import os

SOME_KEY = "0123456789ABCDEF"
SOME_IV  = "0123456789ABCDEF"

'''
def sha1(path):
    hasher = hashlib.sha1()
    try:
        stream = open(path, 'rb')
        hasher.update(stream.read())
        stream.close()
    except IOError:
        return 0
    return hasher.hexdigest()
'''


def sha1(stream):
    stream.seek(0)
    hasher = hashlib.sha1()
    try:
        hasher.update(stream.read())
    except IOError:
        stream.seek(0)
        return 0
    stream.seek(0)
    return hasher.hexdigest()


def decrypt(inBuffer, filename, chunksize=64*1024):
    inBuffer.seek(0)
    decryptor = AES.new(SOME_KEY, AES.MODE_CBC, SOME_IV)
    try:
        origsize = struct.unpack('<Q', inBuffer.read(struct.calcsize('Q')))[0]
    except struct.error:
        origsize = 0
    with open(filename, 'wb') as outfile:
        while True:
            chunk = inBuffer.read(chunksize)
            if len(chunk) == 0:
                break
            outfile.write(decryptor.decrypt(chunk))
        outfile.truncate(origsize)


def encrypt(filename, outbuffer, chunksize=64*1024):
    encryptor = AES.new(SOME_KEY, AES.MODE_CBC, SOME_IV)
    filesize = os.path.getsize(filename)
    outbuffer.write(struct.pack('<Q', filesize))
    with open(filename, 'rb') as infile:
        while True:
            chunk = infile.read(chunksize)
            if len(chunk) == 0:
                break
            elif len(chunk) % 16 != 0:
                chunk += ' ' * (16 - len(chunk) % 16)
            outbuffer.write(encryptor.encrypt(chunk))
    outbuffer.seek(0)
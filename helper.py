import hashlib
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA as CryptoRSA
import struct
import os
import io

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


class RSA:

    def __init__(self, key=None, bits = 2048):
        if key is None:
            self.key = CryptoRSA.generate(bits)
        else:
            self.key = CryptoRSA.importKey(key.decode('hex'))

    def private(self):
        return self.key.exportKey('DER').encode('hex')

    def public(self):
        publicKey = self.key.publickey()
        return publicKey.exportKey('DER').encode('hex')

    def encrypt(self, message):
        cipher = PKCS1_OAEP.new(self.key)
        return cipher.encrypt(message).encode('hex')

    def decrypt(self, message):
        cipher = PKCS1_OAEP.new(self.key)
        return cipher.decrypt(message.decode('hex'))


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

if __name__ == '__main__':
    key = RSA()
    msg = SOME_KEY
    print 'PRIV: '
    priv = key.private()
    print priv
    print 'PUBLIC: '
    print key.public()
    print 'MSG: '
    print msg
    print 'ENCRYPT: '
    encrypt = key.encrypt(msg)
    print encrypt
    print 'DECRYPT: '
    print key.decrypt(encrypt)

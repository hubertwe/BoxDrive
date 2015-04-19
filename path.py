import os

'''
Operating system universal path operations.
Result of each function is Linux like path.
'''

def normalize(path):
    return os.path.normpath(path).replace('\\', '/')


def absolute(prefix, relativePath):
        return normalize(os.path.join(os.path.normpath(prefix),
                                          os.path.normpath(relativePath)))


def relative(prefix, absolutePath):
    prefix = os.path.normpath(prefix)
    absolutePath = os.path.normpath(absolutePath)
    position = absolutePath.find(prefix)
    if position != -1:
        absolutePath = absolutePath[position + len(prefix):]
    absolutePath = normalize(absolutePath)
    if absolutePath[0] == '/':
        return absolutePath[1:]
    else:
        return absolutePath

if __name__ == '__main__':
    print normalize('/var/www/user/')
    print normalize('C:\\var\\www\\user\\')
    print normalize('C:/var/www/user\\')
    print absolute('/var/', 'www/user')
    print absolute('C:\\', '/www/user/')
    print relative('/var', '/var/www/user')
    print relative('/var/', '/www/user/')
    print relative('E:/pwr/BoxDrive/test', 'E:/pwr/BoxDrive/test/c/Nowy folder')

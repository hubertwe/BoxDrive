BoxDrive
======================

###Requirements###
- Python 2.7
- Box python SDK (https://github.com/box/box-python-sdk) - synchronization with Box web api
```
pip install boxsdk
```
- Watchdog module http://pythonhosted.org//watchdog/ - local file system events
```
pip install watchdog
```
- Bottle module http://bottlepy.org/docs/dev/
```
pip install bottle
```

### Todo:
- [x] Remote event (Radek)
- [x] Box event filter (Radek)
- [x] Remote updater (Hubert)
- [x] Local updater (Hubert)
- [x] Fix Observer/Handler (Hubert)

### Issues:
- [ ] Problems with synchronization when fast update/delete files and folders
- [ ] Remote observer always raises 'Update Event' whenever file is created or updated

### Architecture draft ###


```
LOCAL:              REMOTE:
  +----------+       +----------+
  | Observer |       | Observer |
  +----------+       +----------+
       |                  |
      \|/                \|/
  +----------+       +----------+
  | Handler  |       | Handler  |
  +----------+       +----------+
             |       |  
              \_____/
               /   \ 
  +----------+/     \+----------+
  | Updater  |       | Updater  |
  +----------+       +----------+

  - Create
    - dir
    - file
  - Delete
    - dir
    - file
  - Update
    - dir
    - file
  
```            
       

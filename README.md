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
- [ ] Remote event (Radek)
- [ ] Box event filter (Radek)
- [ ] Remote updater (Hubert)
- [ ] Local updater (Hubert)
- [ ] Fix Observer/Handler (Hubert)

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
       

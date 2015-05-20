import wx
import cStringIO
import ConfigParser
import os
from event import EventList
from box import Box
import local
import remote

typeEVT_SETTINGS = wx.NewEventType()
EVT_SETTINGS = wx.PyEventBinder(typeEVT_SETTINGS, 1)

class SettingsEvent(wx.PyCommandEvent):

    def __init__(self):
        wx.PyCommandEvent.__init__(self, typeEVT_SETTINGS, -1)

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

def loadConfig(configPath):
    config = dict()
    rawConfig = ConfigParser.RawConfigParser()
    rawConfig.read(configPath)
    items = rawConfig.items('main')
    for item in items:
        config[item[0]] = item[1]
    return config

def saveConfig(configPath, config):
    fileHandler = open(configPath, 'w+')
    rawConfig = ConfigParser.RawConfigParser()
    rawConfig.add_section('main')
    for key in config:
        rawConfig.set('main', key, config[key])
    rawConfig.write(fileHandler)
    fileHandler.close()

def startRemote(path, box, eventList):
    updater = local.Updater(path, box)
    handler = remote.Handler(updater, box, eventList)
    observer = remote.Observer(handler, box)
    observer.start()
    return observer

def startLocal(path, box, eventList):
    updater = remote.Updater(path, box)
    handler = local.Handler(updater, eventList)
    observer = local.Observer(path, handler)
    observer.start()
    return observer

class TaskBarIcon(wx.TaskBarIcon):

    def __init__(self):
        super(TaskBarIcon, self).__init__()
        print("Look for tray icon :)")
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.Bind(EVT_SETTINGS, self.on_settings_close)
        self.set_icon('img/icon_inactive.png')
        self.configPath = 'config.cfg'
        self.config = loadConfig(self.configPath)
        self.box = Box()
        self.isAppRunning = False
        if not self.check_config():
            self.on_settings(None)
        else:
            self.start_app()

    def check_config(self):
        return bool(os.path.exists(self.config['path']))

    def start_app(self):
        self.eventList = EventList()
        self.remoteObserver = startRemote(self.config['path'], self.box, self.eventList)
        self.localObserver = startLocal(self.config['path'], self.box, self.eventList)
        self.set_icon('img/icon_active.png')
        self.isAppRunning = True

    def stop_app(self):
        if not self.isAppRunning:
            return
        self.set_icon('img/icon_inactive.png')
        self.isAppRunning = False
        self.remoteObserver.stop()
        self.localObserver.stop()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Show settings', self.on_settings)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, 'Crypto Box Drive')

    def on_left_down(self, event):
        print 'Tray icon was left-clicked.'

    def on_settings(self, event):
        settingsWindow = Settings('', self)
        settingsWindow.Centre()
        settingsWindow.Show()

    def on_settings_close(self, event):
        print 'Setting updated!'
        self.config = loadConfig(self.configPath)
        self.stop_app()
        self.start_app()

    def on_exit(self, event):
        dlg = wx.MessageBox(
        "Do you really want to close this application?",
        "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        if dlg == wx.OK:
            self.stop_app()
            self.Destroy()


class Settings(wx.Frame):

    def __init__(self, title, parent):
        wx.Frame.__init__(self, None, title=title, size=(400,300),
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        self.MakeModal(True)
        self.configPath = 'config.cfg'
        self.config = loadConfig(self.configPath)
        self.parent = parent

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        data = open('img/boxlogo.png', 'rb').read()
        stream = cStringIO.StringIO(data)

        bmp = wx.BitmapFromImage(wx.ImageFromStream(stream))
        image = wx.StaticBitmap(panel, -1, bmp)#, (bmp.GetWidth(), bmp.GetHeight()))

        settingsText = pathLabel = wx.StaticText(panel, -1, 'Settings', pos=(200,50))
        font = wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL)
        settingsText.SetFont(font)

        availableEncryptions = ['AES', 'ARC2', 'Blowfish', 'CAST', 'DES', 'DES3 (Triple DES)','IDEA', 'RC5']


        algorithmCBLabel = wx.StaticText(panel, -1, "Algorithm:")
        self.algorithmCB = wx.ComboBox(panel, -1, availableEncryptions[0], (0, 0),
                         (400, -1), availableEncryptions,
                         wx.CB_DROPDOWN)
        self.algorithmCB.SetSelection(availableEncryptions.index(self.config['algorithm']))

        pathLabel = wx.StaticText(panel,-1,"Directory path:")
        self.path = wx.TextCtrl(panel, -1, size=(400, -1))
        self.path.WriteText(self.config['path'])
        self.path.Bind(wx.EVT_LEFT_DOWN, self.OnPathClick);

        sb = wx.StaticBox(panel, -1, "Options")
        sbsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        sbsizer.Add(algorithmCBLabel,0,wx.ALL,0)
        sbsizer.Add(self.algorithmCB,0,wx.ALL,0)
        sbsizer.Add(pathLabel,0,wx.ALL, 0)
        sbsizer.Add(self.path,0,wx.ALL,0)

        box.Add(image,0,wx.ALL,0)
        box.Add(sbsizer,0,wx.EXPAND|wx.ALL,10)

        panel.SetSizer(box)
        panel.Layout()

    def OnPathClick(self,event):
        dlg = wx.DirDialog(self, "Choose a directory:",
                  style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        dlg.SetPath(self.path.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            self.path.Clear()
            self.path.WriteText(dlg.GetPath())

    def OnClose(self, event):
        print 'Will apply settings here..'
        oldConfig = dict(self.config)
        self.config['path'] = self.path.GetValue()
        self.config['algorithm'] = self.algorithmCB.GetStringSelection()
        self.Hide()
        for key in self.config:
            if oldConfig[key] != self.config[key]:
                saveConfig(self.configPath, self.config)
                wx.PostEvent(self.parent, SettingsEvent())
        self.Destroy()
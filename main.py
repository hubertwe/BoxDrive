import local
import remote
from box import Box
import time
import argparse
from event import EventList

import wx
import  cStringIO

ROOT_FOLDER = 'Some:/path/here'

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', nargs=1, required=True,
                        type=str, dest='root_folder',
                        help='Local path which should be synchronized with Box root')
    path = parser.parse_args().root_folder[0]
    print path
    box = Box()
    eventList = EventList()
    remoteObserver = startRemote(path, box, eventList)
    localObserver = startLocal(path, box, eventList)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print 'Stopping observers, please wait!'
            remoteObserver.stop()
            localObserver.stop()
            print 'Bye, bye!'
            break

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

class Settings(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, size=(400,300),style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        

        data = open('boxlogo.png', "rb").read()
        stream = cStringIO.StringIO(data)

        bmp = wx.BitmapFromImage( wx.ImageFromStream( stream ))
        image = wx.StaticBitmap(panel, -1, bmp)#, (bmp.GetWidth(), bmp.GetHeight()))

        settingsText = pathLabel = wx.StaticText(panel,-1,"Settings",pos=(200,50))
        font = wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL)
        settingsText.SetFont(font)

        availableEncryptions = ['AES', 'ARC2', 'Blowfish', 'CAST', 'DES', 'DES3 (Triple DES)','IDEA', 'RC5']

        
        algorithmCBLabel = wx.StaticText(panel, -1, "Algorithm:")
        self.algorithmCB = wx.ComboBox(panel, -1, availableEncryptions[0], (0, 0), 
                         (400, -1), availableEncryptions,
                         wx.CB_DROPDOWN)

        pathLabel = wx.StaticText(panel,-1,"Directory path:")
        self.path = wx.TextCtrl(panel, -1, size=(400, -1))
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
        if dlg.ShowModal() == wx.ID_OK:
            self.path.Clear()
            self.path.WriteText(dlg.GetPath())

    def OnClose(self, event):
        print 'Will apply settings here..'
        self.Destroy()

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self):
        super(TaskBarIcon, self).__init__()
        print("Look for tray icon :)")
        self.set_icon('boxlogo.png')
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

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
        settingsWindow = Settings("")
        settingsWindow.Centre()
        settingsWindow.Show()

    def on_exit(self, event):
        dlg = wx.MessageBox(
        "Do you really want to close this application?",
        "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        if dlg == wx.OK:
            self.Destroy()

def winMain():
    app = wx.App()
    tray = TaskBarIcon()
    app.MainLoop()

if __name__ == "__main__":
    #main()
    winMain()

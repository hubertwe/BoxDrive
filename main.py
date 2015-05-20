from gui import TaskBarIcon, wx

if __name__ == "__main__":
    app = wx.App()
    tray = TaskBarIcon()
    app.MainLoop()

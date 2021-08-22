import wx
from auto_input_core import start_auto_input
import threading


class Auto_Input(wx.Frame):
    is_runnig = False

    def __init__(self, parent, title):
        super(Auto_Input, self).__init__(parent, title=title)

        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        # menu with exit
        fileMenu = wx.Menu()
        fileItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')

        self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)

        menubar = wx.MenuBar()
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        panel = wx.Panel(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        fgs = wx.FlexGridSizer(4, 2, 15, 25)

        content = wx.StaticText(panel, label="送出文字：")
        send_time = wx.StaticText(panel, label="送出時間：")
        delay = wx.StaticText(panel, label="增加延遲(ms)：")
        repeat_time = wx.StaticText(panel, label="送出次數：")

        self.tc_content = wx.TextCtrl(panel)
        self.tc_send_time = wx.TextCtrl(panel)
        self.tc_delay = wx.TextCtrl(panel)
        self.tc_repeat_time = wx.TextCtrl(panel)

        fgs.AddMany([
                    (content), (self.tc_content, 1, wx.EXPAND),
                    (send_time), (self.tc_send_time, 1, wx.EXPAND),
                    (delay), (self.tc_delay, 1, wx.EXPAND),
                    (repeat_time), (self.tc_repeat_time, 1, wx.EXPAND),
                    ])

        # fgs.AddGrowableRow(2, 1)
        fgs.AddGrowableCol(1, 1)

        hbox.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        panel.SetSizer(hbox)

        self.button = wx.Button(panel, wx.ID_ANY, pos=(
            150, 180), size=(200, 20), label="開始執行")

        self.button.Bind(wx.EVT_BUTTON, self.OnButtonClicked)

        self.SetSize((500, 250))
        self.SetTitle('自動輸入文字工具')
        self.Centre()

    def OnQuit(self, e):
        self.Close()

    def OnButtonClicked(self, e):
        if not self.tc_content.GetValue() or \
                not self.tc_send_time.GetValue() or \
                not self.tc_delay.GetValue() or \
                not self.tc_repeat_time.GetValue():
            print('input value missing.')
            return

        if self.is_runnig:
            self.th.do_run = False
            self.button.SetLabel('開始執行')
            self.is_runnig = False
        else:
            print("送出文字", self.tc_content.GetValue())
            print("送出時間", self.tc_send_time.GetValue())
            print("增加延遲", self.tc_delay.GetValue())
            print("送出次數", self.tc_repeat_time.GetValue())
            self.button.SetLabel('結束執行')
            self.is_runnig = True

            # must multi threading
            self.th = threading.Thread(target=start_auto_input, args=(
                self.tc_content.GetValue(),
                self.tc_send_time.GetValue(),
                self.tc_delay.GetValue(),
                self.tc_repeat_time.GetValue()))
            self.th.start()


def main():
    app = wx.App()
    ex = Auto_Input(None, title='Review')
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()

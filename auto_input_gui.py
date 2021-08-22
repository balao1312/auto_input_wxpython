#! /usr/bin/env python3 
##-*- coding: utf-8 -*-

import wx
from auto_input_core import start_auto_input
from auto_input_core import test
import threading
from time import sleep
from datetime import timedelta
import datetime


class Auto_Input(wx.Frame):
    is_running = False

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
        send_time = wx.StaticText(panel, label="送出基準時間：")
        delay = wx.StaticText(panel, label="增加延遲(ms)：")
        repeat_time = wx.StaticText(panel, label="重覆送出次數：")

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

        # start button
        self.button_start = wx.Button(panel, wx.ID_ANY, pos=(
            90, 180), size=(150, 20), label="開始執行")
        self.button_start.Bind(wx.EVT_BUTTON, self.start_button_pressed)

        # stop button
        self.button_stop = wx.Button(panel, wx.ID_ANY, pos=(
            280, 180), size=(150, 20), label="停止執行")
        self.button_stop.Bind(wx.EVT_BUTTON, self.stop_button_pressed)

        # test button
        # self.button_test = wx.Button(panel, wx.ID_ANY, pos=(
        #     400, 180), size=(80, 20), label="測試")
        # self.button_test.Bind(wx.EVT_BUTTON, self.OnButtonClicked_test)

        # output section
        self.output = wx.StaticText(panel, pos=(30, 230), label='')

        self.SetSize((500, 400))
        self.Centre()

    def OnQuit(self, e):
        try:
            self.th.do_run = False
        except:
            pass
        self.Close()

    def validate_input(self):
        # content
        content = self.tc_content.GetValue()
        if not content:
            self.output.SetLabel('錯誤：資料欄位-送出文字 空白')
            return False

        # base_time
        base_time = self.tc_send_time.GetValue()
        if not base_time:
            self.output.SetLabel('錯誤：資料欄位-送出基準時間 空白')
            return False
        # time format check
        try:
            base_time_object = datetime.datetime.strptime(
                base_time, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            self.output.SetLabel('送出基準時間格式有誤，ex: 2021-08-23 08:05:00')
            return False
        # time in future
        past_time_delta = timedelta(seconds=0)
        if base_time_object - datetime.datetime.now() < past_time_delta:
            self.output.SetLabel('送出基準時間有誤，目標時間已過')
            return False

        # delay
        delay = self.tc_delay.GetValue()
        if not delay:
            self.output.SetLabel('錯誤：資料欄位-增加延遲 空白')
            return False
        try:
            delay = int(delay)
        except:
            self.output.SetLabel('增加延遲資料有誤,請輸入數字')
            return False

        # repeat time
        repeat_time = self.tc_repeat_time.GetValue()
        if not repeat_time:
            self.output.SetLabel('錯誤：資料欄位-重覆送出次數 空白')
            return False
        try:
            repeat_time = int(repeat_time)
        except:
            self.output.SetLabel('重覆送出次數資料有誤,請輸入數字')
            return False

        send_time = base_time_object + timedelta(milliseconds=delay)
        return (content, send_time, repeat_time)

    def start_button_pressed(self, e):
        if self.validate_input():
            content, sendtime, repeat_time = self.validate_input()
            self.confirm_msg = f'送出內容： {content}\n' \
                f'送出時間： {sendtime}\n' \
                f'送出重覆次數： {repeat_time}'\
                f'\n-------------------------------\n'\
                f'等待目標時間到達 ...'
            self.output.SetLabel(self.confirm_msg)
        else:
            return

        # fire up
        self.th = threading.Thread(
            target=start_auto_input, args=(content, sendtime, repeat_time))
        self.th.start()

        self.th_check_done = threading.Thread(
            target=self.check_done, args=())
        self.th_check_done.start()

        self.is_running = True

    def stop_button_pressed(self, e):
        try:
            self.th.do_run = False
        except:
            pass
        self.output.SetLabel('已停止')
        self.is_running = False

    def OnButtonClicked_test(self, e):
        msg = '等待目標時間...'
        self.output.SetLabel(msg)
        self.th = threading.Thread(target=test, args=())
        self.th.start()

        self.th_check_done = threading.Thread(
            target=self.check_done, args=())
        self.th_check_done.start()

    def check_done(self):
        while 1:
            if not self.th.is_alive():
                self.confirm_msg += f'\n{"-"*50}'
                self.confirm_msg += '\n完成送出!'
                try:
                    if self.is_running:
                        self.output.SetLabel(self.confirm_msg)
                    self.is_running = False
                except:
                    pass
                break
            sleep(1)


def main():
    app = wx.App()
    ex = Auto_Input(None, title='自動輸入文字工具')
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()

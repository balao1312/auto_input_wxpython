#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import wx
from auto_input_core import start_auto_input
from auto_input_core import test
import threading
from time import sleep
from datetime import timedelta
import datetime
import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')


class MainFrame(wx.Frame):
    is_running = False

    saved_data = Path.home().joinpath('.auto_input_data')
    error_log = Path.home().joinpath('.auto_input_error_log')

    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title)

        self.InitUI()
        self.try_load_save()
        self.Centre()
        self.Show()

    def InitUI(self):
        # menu with exit
        fileMenu = wx.Menu()
        fileItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')

        self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)

        menubar = wx.MenuBar()
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        panel = wx.Panel(self)

        # -------------------------------------------------------------

        # main input section
        fgs = wx.FlexGridSizer(7, 2, 15, 25)

        content_1 = wx.StaticText(panel, label="送出文字 1：")
        content_2 = wx.StaticText(panel, label="送出文字 2：")
        content_3 = wx.StaticText(panel, label="送出文字 3：")
        send_time = wx.StaticText(panel, label="送出基準時間：")
        delay = wx.StaticText(panel, label="增加延遲(ms)：")
        repeat_time = wx.StaticText(panel, label="重覆送出次數：")

        self.tc_content_1 = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.tc_content_2 = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.tc_content_3 = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.tc_send_time = wx.TextCtrl(panel)
        self.tc_delay = wx.TextCtrl(panel)
        self.tc_repeat_time = wx.TextCtrl(panel)

        # fgs.AddGrowableRow(2, 1)
        fgs.AddGrowableCol(1, 1)

        fgs.AddMany([
            (content_1), (self.tc_content_1, 1, wx.EXPAND),
            (content_2), (self.tc_content_2, 1, wx.EXPAND),
            (content_3), (self.tc_content_3, 1, wx.EXPAND),
            (send_time), (self.tc_send_time, 1, wx.EXPAND),
            (delay), (self.tc_delay, 1, wx.EXPAND),
            (repeat_time), (self.tc_repeat_time, 1, wx.EXPAND),
        ])
        # -------------------------------------------------------------

        # horizontal section
        fgs_button = wx.FlexGridSizer(1, 2, 115, 25)

        # get time button
        # self.button_get_default = wx.Button(panel, wx.ID_ANY, label="輸入範本")
        # self.button_get_default.Bind(wx.EVT_BUTTON, self.get_default)

        # start button
        self.button_start = wx.Button(panel, wx.ID_ANY, label="開始執行")
        self.button_start.Bind(wx.EVT_BUTTON, self.start_button_pressed)

        # stop button
        self.button_stop = wx.Button(panel, wx.ID_ANY, label="停止執行")
        self.button_stop.Bind(wx.EVT_BUTTON, self.stop_button_pressed)

        # test button
        # self.button_test = wx.Button(panel, wx.ID_ANY, label="測試")
        # self.button_test.Bind(wx.EVT_BUTTON, self.OnButtonClicked_test_with_fixed_value)

        fgs_button.AddMany(
            [(self.button_start,), (self.button_stop)]
        )
        # -------------------------------------------------------------

        # static output
        fgs_output = wx.FlexGridSizer(1, 1, 1)
        self.output = wx.StaticText(panel, size=(400, 300), label='')

        fgs_output.AddMany(
            [self.output]
        )
        # -------------------------------------------------------------

        # come to mommy
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        vbox.Add(fgs_button, proportion=1, flag=wx.ALL |
                 wx.ALIGN_CENTER_HORIZONTAL, border=15)
        vbox.Add(fgs_output, proportion=1, flag=wx.ALL |
                 wx.ALIGN_CENTER_HORIZONTAL, border=15)
        panel.SetSizer(vbox)

        # output section

        self.SetSize((800, 700))
        self.Centre()

    def OnQuit(self, e):
        try:
            self.th.do_run = False
        except:
            pass

        values = {
            'ct_1': self.tc_content_1.GetValue(),
            'ct_2': self.tc_content_2.GetValue(),
            'ct_3': self.tc_content_3.GetValue(),
            'send_time': self.tc_send_time.GetValue(),
            'delay': self.tc_delay.GetValue(),
            'repeat': self.tc_repeat_time.GetValue()
        }

        # with open(f'{self.application_path}/.auto_input_data', 'wb') as f:
        #     pickle.dump(values, f)

        json.dump(values, open(self.saved_data, 'w', encoding='utf-8'))

        print('==> Column values saved.')
        self.Destroy()

    def validate_input(self):
        content_list = []

        content_1 = self.tc_content_1.GetValue()
        content_2 = self.tc_content_2.GetValue()
        content_3 = self.tc_content_3.GetValue()

        for i in range(1, 4):
            if locals()[f'content_{i}'] != '':
                content_list.append(locals()[f'content_{i}'])

        if not content_list:
            self.output.SetLabel('錯誤：資料欄位-送出文字皆空白')
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
        return (content_list, send_time, repeat_time)

    def start_button_pressed(self, e):
        if self.is_running:
            print('==> Already running.')
            return

        if self.validate_input():
            content, sendtime, repeat_time = self.validate_input()
            self.confirm_msg = f'送出內容： {content}\n' \
                f'送出時間： {sendtime}\n' \
                f'送出重覆次數： {repeat_time}'\
                f'\n{"-"*50}\n'\
                f'等待目標時間到達 ...'
            self.output.SetLabel(self.confirm_msg)
        else:
            return

        # fire up
        self.th = threading.Thread(
            target=start_auto_input, args=(content, sendtime, repeat_time, self), daemon=True)
        self.th.start()

        self.is_running = True

    def stop_button_pressed(self, e):
        try:
            self.th.do_run = False
            print('==> Thread exists, try stopping.')
            sleep(1)
            del self.th
            print('==> Thread deleted.')
        except Exception as e:
            print(e.__class__, e)

        self.output.SetLabel('已停止')
        self.is_running = False

    def OnButtonClicked_test_with_fixed_value(self, e):
        msg = '測試...'
        self.output.SetLabel(msg)
        self.th = threading.Thread(target=test, args=())
        self.th.start()

        self.th_check_done = threading.Thread(
            target=self.check_done, args=())
        self.th_check_done.start()

    def get_default(self, event):
        self.tc_content_1.SetValue('')
        self.tc_content_1.AppendText('1.1\n1.2\n1.3')
        self.tc_content_2.SetValue('')
        self.tc_content_2.AppendText('2.1\n2.2\n2.3')
        self.tc_content_3.SetValue('')
        self.tc_content_3.AppendText('3.1\n3.2\n3.3')

        example_time = (datetime.datetime.now() +
                        timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
        self.tc_send_time.SetLabel(example_time)
        self.tc_delay.SetLabel('0')
        self.tc_repeat_time.SetLabel('3')

    def try_load_save(self):
        try:
            self.values = json.load(
                open(self.saved_data, 'r', encoding='utf-8'))
            print('==> find previous values.')
        except Exception as e:
            print(f'{sys._getframe().f_code.co_name}, {e.__class__}: {e}')
            with open(self.error_log, 'a') as f:
                f.write(f'{sys._getframe().f_code.co_name}, {e.__class__}: {e}')

        try:
            self.values
            print(self.values)
            # format: {'ct_1': '', 'ct_2': '', 'ct_3': '', 'delay': '', 'repeat': '', 'send_time': ''}
            self.tc_content_1.AppendText(self.values['ct_1'])
            self.tc_content_2.AppendText(self.values['ct_2'])
            self.tc_content_3.AppendText(self.values['ct_3'])
            self.tc_send_time.SetLabel(self.values['send_time'])
            self.tc_delay.SetLabel(self.values['delay'])
            self.tc_repeat_time.SetLabel(self.values['repeat'])
        except Exception as e:
            print(f'{sys._getframe().f_code.co_name}, {e.__class__}: {e}')
            with open(self.error_log, 'a') as f:
                f.write(f'{sys._getframe().f_code.co_name}, {e.__class__}: {e}')


def main():
    app = wx.App()
    ex = MainFrame(None, title='自動輸入文字工具')
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()

#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import pyautogui
from time import sleep
from datetime import datetime
from datetime import timedelta
import os


def test():
    delta = timedelta(seconds=5)
    send_time = datetime.now() + delta
    start_auto_input(['1.1\n1.2\n1.3', '2.1\n2.2\n2.3', '3.1\n3.2\n3.3'], send_time, 2)


def start_auto_input(content_list, send_time, repeat_time, frame):

    print('-' * 50)
    print(
        f'send time: {send_time}\nrepeat times: {repeat_time}')
    print('-' * 50)

    # thread object to get 'do_run' key to get stop signal from main process.
    t = threading.current_thread()

    print('start session ...')

    # init pyautogui for later use for no preloading time.
    pyautogui.press('ctrl')
    sleep(0.1)
    pyautogui.press('ctrl')

    # pyautogui.hotkey('command', 'tab')
    # sleep(1)

    # standby at applied_time - 2s
    buffer_time = timedelta(seconds=3)

    while getattr(t, 'do_run', True):
        print('==> Seconds left: ', (send_time - datetime.now()).seconds)

        if send_time - datetime.now() < buffer_time:
            print('==> Standby ...')
            pyautogui.hotkey('command', 'tab', interval=0.1)
            while 1:
                if datetime.now() > send_time:
                    print('==> Time\'s up! Start to send ...')
                    for _ in range(repeat_time):
                        for index, each in enumerate(content_list, start=1):
                            print('sending msg: ', index, 'content: ', each)
                            os.system(f'echo $"{each}" | LANG=en_US.UTF-8 pbcopy')
                            pyautogui.hotkey('command', 'v', interval=0.02)
                            pyautogui.press('enter')

                    frame.confirm_msg += f'\n{"-"*50}'
                    frame.confirm_msg += '\n完成送出!'
                    frame.output.SetLabel(frame.confirm_msg)

                    print('==> Session end.')
                    frame.is_running = False
                    pyautogui.hotkey('command', 'tab', interval=0.1)
                    return

        sleep(1)
    print('==> Stop by clicked button.')
    return

if __name__ == "__main__":
    send_time = datetime.now() + timedelta(seconds=5)
    # send_time = datetime(2021, 8, 29, 23, 45, 20)
    print('target time: ', send_time)
    # start_auto_input(['1\n2\n3', '4\n5\n6', '7\n8\n9'], send_time, 1)




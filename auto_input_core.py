#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import pyautogui
from time import sleep
from datetime import datetime
from datetime import timedelta
import pyperclip


def test():
    delta = timedelta(seconds=5)
    send_time = datetime.now() + delta
    start_auto_input(['1.1\n1.2\n1.3', '2.1\n2.2\n2.3', '3.1\n3.2\n3.3'], send_time, 2)


def start_auto_input(content_list, send_time, repeat_time):

    print('-' * 50)
    print(
        f'send time: {send_time}\nrepeat times: {repeat_time}')
    print('-' * 50)

    # thread object to get 'do_run' key to get stop signal from main process.
    t = threading.current_thread()

    print('start session ...')

    # msg format
    # pyperclip.copy(content_1)
    # sleep(1)

    # init pyautogui for later use for no preloading time.
    pyautogui.press('ctrl')
    sleep(0.1)
    pyautogui.press('ctrl')

    count = 0
    while getattr(t, 'do_run', True):
        count += 1
        print('loop checkpoint, seq=', count)

        # standby at applied_time - 3s
        buffer_time = timedelta(seconds=3)
        if send_time - datetime.now() < buffer_time:
            while 1:
                if datetime.now() > send_time:
                    for _ in range(repeat_time):
                        # press_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                        for each in content_list:
                            pyperclip.copy(each)
                            pyautogui.hotkey('command', 'v', interval=0.015)
                            pyautogui.press('enter')
                        # sent_done_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                        # print(
                            # f'pressed enter at {press_time}, sent at {sent_done_time}')
                    break
            break

        sleep(1)

    print('Session end, enter standby.')

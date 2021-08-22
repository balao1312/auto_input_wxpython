import threading
import pyautogui
from time import sleep
from datetime import datetime
from datetime import timedelta
import subprocess


def copy_osx(text):
    p = subprocess.Popen(['pbcopy', 'w'],
                         stdin=subprocess.PIPE, close_fds=True)
    p.communicate(input=text.encode('utf-8'))


def test():
    delta = timedelta(seconds=5)
    send_time = datetime.now() + delta
    start_auto_input('測試文字', send_time, 5)


def start_auto_input(content, send_time, repeat_time):

    print('-' * 50)
    print(
        f'send time: {send_time}\nrepeat times: {repeat_time}')
    print('-' * 50)

    t = threading.current_thread()
    print('start auto input ...')
    copy_osx(content)
    sleep(1)

    # init pyautogui for later use for no preloading time.
    pyautogui.press('shift')
    sleep(0.1)
    pyautogui.press('shift')

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
                        press_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                        pyautogui.hotkey('command', 'v', interval=0.03)
                        pyautogui.press('enter')
                        sent_done_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                        print(
                            f'pressed enter at {press_time}, sent at {sent_done_time}')
                    break
            break

        sleep(1)

    print('Session end, enter standby.')

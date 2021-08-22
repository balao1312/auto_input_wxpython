import threading
import pyautogui
from time import sleep
from datetime import datetime
import subprocess

def copy_osx(text):
    p = subprocess.Popen(['pbcopy', 'w'],
                         stdin=subprocess.PIPE, close_fds=True)
    p.communicate(input=text.encode('utf-8'))


def paste_osx():
    p = subprocess.Popen(['pbpaste', 'r'],
                         stdout=subprocess.PIPE, close_fds=True)
    stdout, stderr = p.communicate()
    return stdout.decode('utf-8', pos=(
            30, 120),)

def start_auto_input(content, send_time, delay, repeat_time):
    t = threading.current_thread()
    print('start auto input ...')
    copy_osx(content)

    # init pyautogui for later use due to delay problem.
    pyautogui.press('shift')

    while getattr(t, 'do_run', True):
        print('loop start')
        if datetime.now().second % 10 == 5:
            pyautogui.hotkey('command', 'v')

            while 1:
                if datetime.now().second % 10 == 0:
                    press_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    pyautogui.press('enter')
                    sent_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    print(
                        f'msg pressed enter at {press_time}, sent at {sent_time}')
                    break
        sleep(1)

    print('Auto input stoped.')

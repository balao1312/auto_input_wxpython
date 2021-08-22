import subprocess


def copy_osx(text):
    p = subprocess.Popen(['pbcopy', 'w'],
                         stdin=subprocess.PIPE, close_fds=True)
    p.communicate(input=text.encode('utf-8'))

    # proc1 = subprocess.Popen(['echo', '雲開見月'], stdout=subprocess.PIPE)
    # proc2 = subprocess.Popen(['pbcopy'], stdin=proc1.stdout) 
    # p.communicate(input=text.encode('utf-8'))

copy_osx('測試一二三')

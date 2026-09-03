import os
import sys
import time

PYTHON = sys.executable

with open('autorestart.txt', 'w') as f:
    f.write('delete this file to stop auto restarting')

while os.path.isfile('autorestart.txt'):
    print('updating...')
    res = os.system('git pull')
    if res:
        print(f"unable to access git, wait a minute ({res})...")
        time.sleep(60)
        continue
    res = os.system(
        f'{PYTHON} -m pip install --upgrade pip -r requirements.txt')
    if res:
        print(f"unable to update packages, wait a minute ({res})...")
        time.sleep(60)
        continue
    print('starting...')
    os.system(f'{PYTHON} main.py')
    print('stopped')
    print('restarting in')
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

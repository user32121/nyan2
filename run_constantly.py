import os
import sys

PYTHON = sys.executable

with open('autorestart.txt', 'w') as f:
    f.write('delete this file to stop auto restarting')

while os.path.isfile('autorestart.txt'):
    print('updating...')
    os.system(f'{PYTHON} -m pip install --upgrade pip -r requirements.txt')
    print('starting...')
    os.system(f'{PYTHON} main.py')
    print('stopped')

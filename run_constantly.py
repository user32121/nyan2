import os

with open('autorestart.txt', 'w') as f:
    f.write('delete this file to stop auto restarting')

while os.path.isfile('autorestart.txt'):
    print('starting...')
    os.system('python3 main.py')
    print('stopped')

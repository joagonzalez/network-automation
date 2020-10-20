import os
import time

cmd = 'ansible-playbook playbook.yaml'

while True:
    os.system(cmd)
    print('esperamos 10 segundos para otro muestreo...')
    time.sleep(10)
# loop script to gather infromation from sbcs with ansible 

#!/usr/bin/env python3
import os
import time

cmd = "ansible-playbook sbc_audiocodes_telnet.yaml"

while True:
    print("Running ansible playbook to gather sbc information...\n")
    os.system(cmd)
    
    time.sleep(20)

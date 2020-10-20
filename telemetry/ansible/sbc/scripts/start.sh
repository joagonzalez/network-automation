#!/bin/bash

#export http_proxy="http://10.132.64.22:3128"
#export https_proxy="http://10.132.64.22:3128"

# path relativos a la carpeta de script
/usr/bin/python3 ./network-telemetry.py >> ../log/cron.log &

exit 0

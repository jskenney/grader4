#!/usr/bin/env bash

# if the file /tmp/stopsubmit does not exist
# keep restarting the server (useful if this
# script is started via cron)
while [ ! -f /tmp/stopsubmit ]
do
  echo "Fix Permissions Just In Case"
  chmod 644 *.py README
  chmod 755 server.py client.py
  echo "Running Server"
  python3 -B server.py
  echo "restarting server in 10 seconds"
  sleep 10
done

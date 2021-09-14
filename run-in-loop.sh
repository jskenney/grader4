#!/usr/bin/env bash

while true
do
  echo "Fix Permissions Just In Case"
  chmod 644 *.py Dockerfile README
  chmod 755 server.py client.py
  echo "Running Server"
  python3 -B server.py
  echo "restarting server in 10 seconds"
  sleep 10
done

#!/usr/bin/env bash

echo "Fix Permissions Just In Case"
chmod 644 *.py README
chmod 755 server.py client.py

while true
echo "Running Server"
do
  docker run --rm $(docker build -q .)
  echo "restarting server in 5 seconds"
  sleep 5
done

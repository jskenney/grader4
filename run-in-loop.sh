#!/usr/bin/env bash

while true
do
  echo "Running Server"
  python3 server.py
  echo "restarting server in 10 seconds"
  sleep 10
done

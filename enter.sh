#!/bin/bash

echo """
usage: client.py [-h] [--course COURSE] [--project PROJECT] [--base DOCKERBASE] [--user USER] [--rulename RULENAME] [--storedir STORDIR]

Autograde an available job.

options:
  -h, --help           show this help message and exit
  --course COURSE      select a specific course
  --project PROJECT    select a specific project
  --base DOCKERBASE    select default docker image
  --user USER          select a user to process
  --rulename RULENAME  select a specific testcase to run
  --storedir STORDIR   set a specific output location for downloads

Example:

   python3 client.py --storedir zzz --base cs-base --course X --project X --user m2x --rulename x

"""

docker run -it --rm $(docker build -q .) bash

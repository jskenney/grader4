#!/bin/bash

docker rm $(docker ps -a -q)
docker rmi $(docker images -q)


docker build -t cs-base .

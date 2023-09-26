#!/bin/bash

# Remove all existing docker images
# This is dangerous if there is more than one base
docker rm $(docker ps -a -q)
docker rmi $(docker images -q)
docker system prune -a -f

# Build this image
docker build -t cs-base .

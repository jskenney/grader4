#!/bin/bash

###############################################################################
# Delete all docker containers and images do:
docker rm $(docker ps -a -q)
docker rmi $(docker images -q)
docker system prune -a -f

###############################################################################
# Build the environments
pushd cs-base
./build.sh
popd

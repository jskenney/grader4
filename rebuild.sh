#!/bin/bash

echo "Delete previous docker images"
docker rm $(docker ps -a -q)
docker rmi $(docker images -q)

echo "Build new images"
pushd cs-base
docker build -t cs-base .
popd

echo "You can now start the docker grader client"

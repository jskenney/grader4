#!/bin/bash

# requires sudo

docker run -i -t --rm $(docker build -q .)

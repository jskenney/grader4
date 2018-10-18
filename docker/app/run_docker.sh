#!/bin/bash

# requires sudo

docker run --rm $(docker build -q .)

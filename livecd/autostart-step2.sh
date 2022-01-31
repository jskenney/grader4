#!/bin/bash

/usr/bin/tmux new-session -s grader '/usr/bin/docker run --rm -it ubuntu'

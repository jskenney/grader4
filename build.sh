#!/bin/bash

rm -f /tmp/grader-update.sh
touch /tmp/stopsubmit

cat << EOF > /tmp/grader-update.sh
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

echo 'did it work cs-base?'
read foo

pushd db-base
./build.sh
popd

echo 'did it work db-base?'
read foo

rm -f /tmp/stopsubmit
EOF

chmod 755 /tmp/grader-update.sh

tmux attach -t grader
tmux new-session -s grader /tmp/grader-update.sh

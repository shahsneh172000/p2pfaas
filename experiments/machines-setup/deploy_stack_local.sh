#!/bin/bash
# remove the stack if already present
docker stack rm p2p-faas

# create dirs
mkdir -p ~/.config/p2pfaas/discovery
mkdir -p ~/.config/p2pfaas/scheduler

# deploy the stack
cd ../../
cd stack-discovery
docker build -t discovery:latest .
cd ..
cd stack-scheduler
docker build -t scheduler:latest .
cd ..
cd stack

docker stack rm p2p-faas
docker stack rm p2p-fog # temporary

if [ $(uname -m | cut -b 1-3) == "arm" ]
then
    echo "==> ARM architecture detected"
    docker stack deploy -c docker-compose-local.armhf.yml p2p-faas
else 
    docker stack deploy -c docker-compose-local.yml p2p-faas
fi
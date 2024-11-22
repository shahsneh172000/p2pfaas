#!/bin/bash
# login
docker login registry.gitlab.com -u "gitlab+deploy-token-64025" -p "CfNK37-zH4oV1xDstDe6"
docker login registry.gitlab.com -u "gitlab+deploy-token-64030" -p "zNCW2p4iJG6CpPsxnnqx"

cd ../../
cd stack

docker stack rm p2p-fog
docker stack deploy -c docker-compose.yml p2p-fog

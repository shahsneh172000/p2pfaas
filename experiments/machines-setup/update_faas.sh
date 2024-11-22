#!/bin/bash
# Update the openfaas distribution
cd ../../../
cd faas

# update
git checkout $(git rev-parse --abbrev-ref HEAD) --force
git pull
git checkout tags/0.20.5

# undeploy
docker stack rm func
# wait stack to be deleted completely
until [[ -z $(docker stack ps func -q) ]]; do sleep 1; done

# create simple secrets
docker secret rm basic-auth-password
docker secret rm basic-auth-user

echo "admin" | docker secret create basic-auth-password -
echo "admin" | docker secret create basic-auth-user -

# re-deploy faas
./deploy_stack.sh

# install faas-cli
echo "==> Downloading faas-cli"
rm -rfv ~/bin/faas-cli

mkdir ~/bin
if [ $(uname -m | cut -b 1-3) == "arm" ]
then
    echo "==> ARM architecture detected"
    wget https://github.com/openfaas/faas-cli/releases/download/0.12.14/faas-cli-armhf -O ~/bin/faas-cli
else
    wget https://github.com/openfaas/faas-cli/releases/download/0.12.14/faas-cli -O ~/bin/faas-cli
fi

# make runnable
chmod +x ~/bin/faas-cli

echo "==> Done"

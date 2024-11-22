#!/bin/bash
cd ..
echo "==> Pulling..."
git checkout $(git rev-parse --abbrev-ref HEAD) --force
git pull
cd ../stack
echo "==> Pulling stack..."
git checkout $(git rev-parse --abbrev-ref HEAD) --force
git pull
echo "==> Pulling scheduler..."
cd ../stack-scheduler
git checkout $(git rev-parse --abbrev-ref HEAD) --force
git pull
echo "==> Pulling discovery..."
cd ../stack-discovery
git checkout $(git rev-parse --abbrev-ref HEAD) --force
git pull

#!/bin/bash
docker-compose down
rm -rfv ./ganglia/*
docker-compose up -d

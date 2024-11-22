#!/bin/bash
FAAS_CLI=~/bin/faas-cli

cd ../functions/pigo-openfaas-f
$FAAS_CLI login -u admin --password admin
$FAAS_CLI remove pigo-face-detector-f
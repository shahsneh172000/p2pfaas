#!/bin/bash
FAAS_CLI=~/bin/faas-cli

# deploy pigo fake function
cd ../functions/pigo-openfaas-f
$FAAS_CLI login -u admin --password admin
$FAAS_CLI build
$FAAS_CLI deploy
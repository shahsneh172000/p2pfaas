#!/bin/bash
FAAS_CLI=~/bin/faas-cli

cd ../functions/exponential-loop
$FAAS_CLI login -u admin --password admin
$FAAS_CLI build
$FAAS_CLI deploy
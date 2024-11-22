#!/bin/bash
./benchmark \
    -hosts-file "./hosts.txt" \
    -function-name "fn-pigo" \
    -dir-payloads "./blobs" \
    -payloads "familyr_320p.jpg" \
    -payloads-mix-percentages "1.0" \
    -lambdas "2,3,4,5,6,7,7,8,9,10,11,12" \
    -benchmark-time "3600" \
    -dir-log "./log" \
    -traffic-model-type "static" \
    -learning-reward-deadlines "10" \
    -learning-set-reward \
    -learning-batch-size "20" \
    -learning # \
#    -debug 


# -poisson "true" \


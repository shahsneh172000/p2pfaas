#!/bin/bash
./benchmark \
    -hosts-file "./hosts.txt" \
    -function-name "fn-pigo" \
    -dir-payloads "./blobs" \
    -payloads "familyr_320p.jpg,familyr_100p.jpg" \
    -payloads-mix-percentages "0.30,0.70" \
    -lambdas "4,6,8,12,13,14,15,16,17,18,19,20" \
    -benchmark-time "3600" \
    -dir-log "./log" \
    -traffic-model-type "static" \
    -learning-reward-deadlines "0.194,0.045" \
    -learning-set-reward \
    -learning-batch-size "20" \
    -learning # \
#    -debug 


# -poisson "true" \

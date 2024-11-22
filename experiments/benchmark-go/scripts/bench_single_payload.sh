#!/bin/bash
./benchmark \
    -hosts-file "./hosts.txt" \
    -function-name "fn-pigo" \
    -dir-payloads "./blobs" \
    -payloads "familyr_320p.jpg" \
    -payloads-mix-percentages "1.0" \
    -lambdas "2,3,4,5,6,7,2,3,4,5,6,7" \
    -benchmark-time "500" \
    -dir-log "./log" \
    -traffic-model-type "static" \
    -learning-reward-deadlines "0.25" \
    -learning-set-reward \
    -learning-batch-size "20" \
    -learning # \
    # -debug 


# -poisson "true" \

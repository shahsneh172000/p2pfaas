#!/bin/bash
./benchmark \
    -hosts-file "./hosts.txt" \
    -function-name "fn-pigo" \
    -dir-payloads "./blobs" \
    -payloads "familyr_320p.jpg,familyr_100p.jpg" \
    -payloads-mix-percentages "0.50,0.50" \
    -benchmark-time "7200" \
    -dir-log "./log" \
    -traffic-model-dir "./traffic" \
    -traffic-model-type "dynamic" \
    -traffic-model-file-prefix "traffic_node_" \
    -traffic-model-file-extension "csv" \
    -traffic-model-shift "0.0" \
    -traffic-model-repetitions "2.0" \
    -traffic-model-min-load "0.0" \
    -traffic-model-max-load "30.0" \
    -traffic-generation-distribution "deterministic" \
    -learning-reward-deadlines "0.18825,0.07495" \
    -learning-set-reward \
    -learning-batch-size "10" \
    -learning # \
    # -debug 


# -poisson "true" \

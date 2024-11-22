#!/bin/bash
rm -rfv benchmark
cd ../src/benchmark
go build -v
mv benchmark ../../scripts
#!/usr/bin/env bash

set -eu

source "${GATE_UTILS}"

log Reporting env

env | sort | tee -a "${LOG_FILE}"

log Testing disk IO

fio \
    --randrepeat=1 \
    --ioengine=libaio \
    --direct=1 \
    --gtod_reduce=1 \
    --name=test \
    --filename=.fiotest \
    --bs=4k \
    --iodepth=64 \
    --size=500M \
    --readwrite=randrw \
    --rwmixread=50

#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../../..)}

INPUT_DIR=tools/virsh/tmpgate/config
OUTPUT_DIR=tools/virsh/tmpgate/scripts

IMAGE_PROMENADE=${IMAGE_PROMENADE:-quay.io/attcomdev/promenade:latest}

mkdir -p $OUTPUT_DIR
echo === Generating updated certificates ===
docker run --rm -t \
    -w /target \
    -e PROMENADE_DEBUG=1 \
    -v $WORKSPACE:/target \
    ${IMAGE_PROMENADE} \
        promenade \
            build-all \
                --validators \
                -o $OUTPUT_DIR \
                $INPUT_DIR/*.yaml

#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../../..)}

OUTPUT_DIR=$WORKSPACE/tools/virsh/tmpgate/config
echo "OD=$OUTPUT_DIR"

IMAGE_PROMENADE=${IMAGE_PROMENADE:-quay.io/attcomdev/promenade:latest}

mkdir -p $OUTPUT_DIR

echo --- Copying configuration ---
cp $WORKSPACE/example/*.yaml $OUTPUT_DIR

echo --- Generating updated certificates ---
docker run --rm -t \
    -w /target \
    -e PROMENADE_DEBUG=1 \
    -v $OUTPUT_DIR:/target \
    ${IMAGE_PROMENADE} \
        promenade \
            generate-certs \
                -o /target \
                $(ls $OUTPUT_DIR)

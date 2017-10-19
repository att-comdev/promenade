#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../../..)}

IMAGE_PROMENADE=${IMAGE_PROMENADE:-quay.io/attcomdev/promenade:latest}

sudo docker build -t $IMAGE_PROMENADE $WORKSPACE

#!/usr/bin/env bash

set -eux

IMAGE_PROMENADE=${IMAGE_PROMENADE:-quay.io/attcomdev/promenade:latest}

SCRIPT_DIR=$(realpath $(dirname $0))
CONFIG_SOURCE=${1:-$(realpath ${SCRIPT_DIR}/../examples/basic)}
BUILD_DIR=${2:-$(realpath ${SCRIPT_DIR}/../build)}

echo === Cleaning up old data ===
rm -rf ${BUILD_DIR}
mkdir -p ${BUILD_DIR}

cp "${CONFIG_SOURCE}"/*.yaml ${BUILD_DIR}

echo === Generating updated certificates ===
docker run --rm -t \
    -w /target \
    -e PROMENADE_DEBUG=$PROMENADE_DEBUG \
    -v ${BUILD_DIR}:/target \
    ${IMAGE_PROMENADE} \
        promenade \
            generate-certs \
                -o /target \
                $(ls ${BUILD_DIR})

echo === Building bootstrap scripts ===
docker run --rm -t \
    -w /target \
    -e PROMENADE_DEBUG=$PROMENADE_DEBUG \
    -v ${BUILD_DIR}:/target \
    ${IMAGE_PROMENADE} \
        promenade \
            build-all \
                -o /target \
                --validators \
                $(ls ${BUILD_DIR})

echo === Done ===

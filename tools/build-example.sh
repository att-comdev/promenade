#!/usr/bin/env bash

set -ex

echo === Cleaning up old data ===
rm -rf configs
mkdir configs

echo === Generating updated certificates ===
docker run --rm -t \
    -w /target \
    -e PROMENADE_DEBUG=$PROMENADE_DEBUG \
    -v $(pwd):/target quay.io/attcomdev/promenade:latest \
        promenade \
            generate-certs \
                -o example \
                example/*.yaml

echo === Building bootstrap scripts ===
docker run --rm -t \
    -w /target \
    -e PROMENADE_DEBUG=$PROMENADE_DEBUG \
    -v $(pwd):/target quay.io/attcomdev/promenade:latest \
        promenade \
            build-all \
                -o configs \
                example/*.yaml

echo === Done ===

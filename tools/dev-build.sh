#!/usr/bin/env bash

set -ex

echo === Cleaning up old data ===
rm -rf promenade.tar configs
mkdir configs

echo === Building image ===
docker build -t quay.io/attcomdev/promenade:latest .

echo === Generating updated certificates ===
docker run --rm -t \
    -w /target \
    -v $(pwd):/target quay.io/attcomdev/promenade:latest \
        promenade -v \
            generate-certs \
                -o example \
                example/*.yaml

echo === Building bootstrap scripts ===
docker run --rm -t \
    -w /target \
    -v $(pwd):/target quay.io/attcomdev/promenade:latest \
        promenade -v \
            build-all \
                -o configs \
                example/*.yaml

echo === Done ===

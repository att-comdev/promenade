#!/usr/bin/env bash

set -eux

SCRIPT_DIR=$(realpath $(dirname $0))
SOURCE_DIR=$(realpath $SCRIPT_DIR/../..)

echo === Building image ===
docker build -t quay.io/attcomdev/promenade:latest ${SOURCE_DIR}

export PROMENADE_DEBUG=${PROMENADE_DEBUG:-1}

exec docker run \
    --rm -it \
    --publish 9000:9000 \
    --paste config:/etc/promenade/api-paste.ini \
    --volume "${SOURCE_DIR}/etc/promenade":/etc/promenade \
    quay.io/attcomdev/promenade:latest \
        server

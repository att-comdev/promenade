#!/usr/bin/env bash

set -ex

echo === Building image ===
docker build -t quay.io/attcomdev/promenade:latest .

export PROMENADE_DEBUG=${PROMENADE_DEBUG:-1}

exec $(dirname $0)/build-example.sh

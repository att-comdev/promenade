#!/usr/bin/env bash

set -eu

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=$(realpath ${SCRIPT_DIR}/../../..)
GATE_UTILS=${WORKSPACE}/tools/g2/lib/all.sh

source ${GATE_UTILS}

docker_build_promenade

log Killing Promenade pods
for pod in $(kubectl_cmd "${GENESIS_NAME}" -n ucp get pod | grep promenade | awk '{print $1}'); do
    kubectl_cmd "${GENESIS_NAME}" -n ucp delete pod "${pod}"
done

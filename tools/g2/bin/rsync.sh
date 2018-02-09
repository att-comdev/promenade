#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=$(realpath ${SCRIPT_DIR}/../../..)
GATE_UTILS=${WORKSPACE}/tools/g2/lib/all.sh
TEMP_DIR=${TEMP_DIR:-$(mktemp -d)}

source ${GATE_UTILS}

exec rsync -e "ssh -F ${SSH_CONFIG_DIR}/config" $@

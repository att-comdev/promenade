#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../../..)}

$WORKSPACE/tools/virsh/ssh.sh n0 /root/promenade/validate-genesis.sh

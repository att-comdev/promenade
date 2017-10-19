#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../..)}

API=${1:-n0}

$SCRIPT_DIR/ssh.sh $API /root/promenade/validate-cluster.sh

#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../../..)}

$WORKSPACE/tools/virsh/stop.sh
$WORKSPACE/tools/virsh/start.sh

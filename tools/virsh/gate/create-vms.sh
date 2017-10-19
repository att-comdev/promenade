#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../../..)}

$WORKSPACE/tools/virsh/destroy.sh
$WORKSPACE/tools/virsh/create.sh
$WORKSPACE/tools/virsh/push-example-scripts.sh

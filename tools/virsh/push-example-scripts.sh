#!/usr/bin/env bash

set -ex

VMS=${@:-n0 n1 n2 n3}

SCRIPT_DIR=$(realpath $(dirname $0))
EXAMPLE_PATH=$(realpath ${SCRIPT_DIR}/../../example)


for vm in $VMS; do
    $SCRIPT_DIR/rsync.sh $EXAMPLE_PATH/scripts/* $vm:/root/promenade &
done

wait

#!/usr/bin/env bash

set -e

VMS=${@:-n0 n1 n2 n3}

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../../..)}

$WORKSPACE/tools/virsh/destroy.sh
$WORKSPACE/tools/virsh/create.sh

for vm in $VMS; do
    $WORKSPACE/tools/virsh/rsync.sh $WORKSPACE/tools/virsh/tmpgate/scripts/* $vm:/root/promenade &
done

wait

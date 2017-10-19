#!/usr/bin/env bash

set -ex
set -o pipefail

VMS=${@:-n0 n1 n2 n3}

SCRIPT_DIR=$(realpath $(dirname $0))

start_vm() {
    NAME=$1

    virsh start $NAME
    set +x
    while ! $SCRIPT_DIR/ssh.sh $NAME /bin/true; do
        sleep 0.5
    done
    echo Node $NAME started
    set -x
}


for vm in $VMS; do
    start_vm $vm &
done

wait

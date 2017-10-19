#!/usr/bin/env bash

set -ex
set -o pipefail

VMS=${@:-n0 n1 n2 n3}

SCRIPT_DIR=$(realpath $(dirname $0))


for vm in $VMS; do
    virsh destroy $vm &
done

wait

#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../../..)}

if [ $# -le 0 ]; then
    echo "Must specify at least one vm to join"
    exit 1
fi

for vm in $@; do
    $WORKSPACE/tools/virsh/ssh.sh $vm /root/promenade/join-$vm.sh
    $WORKSPACE/tools/virsh/ssh.sh $vm /root/promenade/validate-$vm.sh
done

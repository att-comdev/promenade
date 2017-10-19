#!/usr/bin/env bash

set -ex

VMS=${@:-n0 n1 n2 n3}

stop_vm() {
    DOMAIN=$1
    if virsh desc $DOMAIN; then
        virsh destroy $DOMAIN
        virsh undefine --remove-all-storage --domain $DOMAIN
    fi
}

for vm in $VMS; do
    stop_vm $vm &
done

wait

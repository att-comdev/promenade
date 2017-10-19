#!/usr/bin/env bash

set -ex

SCRIPT_DIR=$(realpath $(dirname $0))

$SCRIPT_DIR/stop.sh

# Delete base volume
if virsh vol-key --pool default --vol promenade-base.img ; then
    virsh vol-delete $(virsh vol-key --pool default --vol promenade-base.img)
fi

# Delete the network
if virsh net-list --name | grep ^promenade$ ; then
    virsh net-destroy promenade
fi

# Remove ssh keys
rm -rf $SCRIPT_DIR/config-ssh

# Cleanup isos
rm -rf $SCRIPT_DIR/isos

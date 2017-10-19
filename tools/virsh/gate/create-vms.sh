#!/usr/bin/env bash

set -e

VMS=${@:-n0 n1 n2 n3}

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../../..)}

BASE_IMAGE_URL=https://cloud-images.ubuntu.com/releases/16.04/release/ubuntu-16.04-server-cloudimg-amd64-disk1.img

if ! virsh vol-key --pool default --vol promenade-base.img; then
    pushd $(mktemp -d)
    curl -L -o base.img $BASE_IMAGE_URL
    if ! virsh pool-info default; then
        virsh pool-create-as --name default --type dir --target /var/lib/libvirt/images
    fi
    virsh vol-create-as \
        --pool default \
        --name promenade-base.img \
        --format qcow2 \
        --capacity 68719476736 \
        --prealloc-metadata

    virsh vol-upload \
        --vol promenade-base.img \
        --file base.img \
        --pool default
    popd
fi

$WORKSPACE/tools/virsh/destroy.sh
$WORKSPACE/tools/virsh/create.sh

for vm in $VMS; do
    $WORKSPACE/tools/virsh/rsync.sh $WORKSPACE/tools/virsh/tmpgate/scripts/* $vm:/root/promenade &
done

wait

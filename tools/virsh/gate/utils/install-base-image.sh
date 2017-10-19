#!/usr/bin/env bash

set -ex
set -o pipefail

SOURCE_URL=https://cloud-images.ubuntu.com/releases/16.04/release/ubuntu-16.04-server-cloudimg-amd64-disk1.img

if ! virsh vol-key --pool default --vol promenade-base.img; then
    pushd $(mktemp -d)
    curl -L -o base.img $SOURCE_URL
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

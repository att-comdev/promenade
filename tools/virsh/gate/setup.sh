#!/usr/bin/env bash

set -ex
set -o pipefail

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../../..)}

SOURCE_URL=https://cloud-images.ubuntu.com/releases/16.04/release/ubuntu-16.04-server-cloudimg-amd64-disk1.img

sudo DEBIAN_FRONTEND=noninteractive apt install -y curl genisoimage libvirt-bin virtinst

if ! groups | grep libvirtd; then
    sudo adduser `id -un` libvirtd
    TMP_GROUP=$(id -g)
    newgrp libvirtd
    newgrp $TMP_GROUP
fi

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

SSH_CONFIG_DIR=$WORKSPACE/tools/virsh/config-ssh
mkdir -p ${SSH_CONFIG_DIR}

if [ ! -s ${SSH_CONFIG_DIR}/id_rsa ]; then
    ssh-keygen -N '' -f ${SSH_CONFIG_DIR}/id_rsa
fi

if [ ! -s ${SSH_CONFIG_DIR}/config ]; then
    env -i \
        SSH_CONFIG_DIR=$SSH_CONFIG_DIR \
        envsubst < $WORKSPACE/tools/virsh/templates/ssh-config.sub > ${SSH_CONFIG_DIR}/config
fi

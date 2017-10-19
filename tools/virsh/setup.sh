#!/usr/bin/env bash

set -ex

SCRIPT_DIR=$(realpath $(dirname $0))

SOURCE_URL=https://cloud-images.ubuntu.com/releases/16.04/release/ubuntu-16.04-server-cloudimg-amd64-disk1.img

sudo DEBIAN_FRONTEND=noninteractive apt install -y curl genisoimage libvirt-bin virtinst

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

SSH_CONFIG_DIR=${SCRIPT_DIR}/config-ssh
mkdir -p ${SSH_CONFIG_DIR}
ssh-keygen -N '' -f ${SSH_CONFIG_DIR}/id_rsa
env -i \
    SSH_CONFIG_DIR=${SSH_CONFIG_DIR} \
    envsubst < ${SCRIPT_DIR}/templates/ssh-config.sub > ${SSH_CONFIG_DIR}/config

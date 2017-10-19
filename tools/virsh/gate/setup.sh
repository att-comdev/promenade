#!/usr/bin/env bash

set -ex
set -o pipefail

SCRIPT_DIR=$(realpath $(dirname $0))
WORKSPACE=${WORKSPACE:-$(realpath $SCRIPT_DIR/../../..)}

sudo DEBIAN_FRONTEND=noninteractive apt install -y \
    curl \
    docker.io \
    genisoimage \
    libvirt-bin \
    virtinst

for grp in docker libvirtd; do
    if ! groups | grep $grp; then
        sudo adduser `id -un` $grp
    fi
done

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

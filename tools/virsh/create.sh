#!/usr/bin/env bash

set -ex
set -o pipefail

VMS=${@:-n0 n1 n2 n3}

SCRIPT_DIR=$(realpath $(dirname $0))

install_network() {
    if ! virsh net-list --name | grep ^promenade$ ; then
        virsh net-create $SCRIPT_DIR/xml/network.xml
    fi
}

create_vm() {
    set +x
    NAME=$1
    IP=192.168.77.1${1:1}

    ISO_DIR=$SCRIPT_DIR/iso/$NAME
    rm -rf $ISO_DIR
    mkdir -p $ISO_DIR
    pushd $ISO_DIR

    export BR_IP_NODE=$IP
    export SSH_PUBLIC_KEY=$(cat ${SCRIPT_DIR}/config-ssh/id_rsa.pub)

    if virsh vol-list --pool default | grep promenade-$NAME.img ; then
        virsh vol-delete --pool default promenade-$NAME.img
    fi

    virsh vol-create-as \
        --pool default \
        --name promenade-$NAME.img \
        --capacity 64G \
        --format qcow2 \
        --backing-vol promenade-base.img \
        --backing-vol-format qcow2

    ISO_IMAGE=$ISO_DIR/cidata.iso
    env envsubst < $SCRIPT_DIR/templates/user-data.sub > user-data
    env envsubst < $SCRIPT_DIR/templates/meta-data.sub > meta-data
    env envsubst < $SCRIPT_DIR/templates/network-config.sub > network-config
    genisoimage \
        -V cidata \
        -input-charset utf-8 \
        -joliet \
        -rock \
        -o $ISO_IMAGE \
            meta-data \
            network-config \
            user-data

    virt-install \
        --name $NAME \
        --cpu host \
        --graphics vnc,listen=0.0.0.0 \
        --noautoconsole \
        --network network=promenade \
        --vcpus 2 \
        --memory 2048 \
        --import \
        --disk vol=default/promenade-$NAME.img,format=qcow2,bus=virtio \
        --disk pool=default,size=20,format=qcow2,bus=virtio \
        --disk pool=default,size=20,format=qcow2,bus=virtio \
        --disk $ISO_IMAGE,device=cdrom

    popd

    while ! $SCRIPT_DIR/ssh.sh $NAME /bin/true; do
        sleep 0.5
    done
    $SCRIPT_DIR/ssh.sh $NAME sync
    echo Node $NAME created
    set -x
}

install_network

for vm in $VMS; do
    create_vm $vm &
done

wait

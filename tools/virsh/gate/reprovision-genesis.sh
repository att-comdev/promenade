#!/usr/bin/env bash

set -ex

SCRIPT_DIR=$(realpath $(dirname $0))

TARGET=$1
API=$2

if [ "x$TARGET" = "x" ]; then
    echo The first argument must be the node to reprovision 1>&2
    exit 1
fi

if [ "x$API" = "x" ]; then
    echo The second argument must be a working node from which to run kubectl 1>&2
    exit 1
fi

if [ $TARGET = $API ]; then
    echo The target and api nodes cannot be the same 1>&2
    exit 1
fi

$WORKSPACE/tools/virsh/ssh.sh $TARGET promenade-teardown
$WORKSPACE/tools/virsh/ssh.sh $API kubectl delete node $TARGET

$WORKSPACE/tools/virsh/destroy.sh $TARGET
$WORKSPACE/tools/virsh/create.sh $TARGET

$WORKSPACE/tools/virsh/rsync.sh $WORKSPACE/tools/virsh/tmpgate/scripts/* $TARGET:/root/promenade

$WORKSPACE/tools/virsh/ssh.sh $TARGET /root/promenade/join-$TARGET.sh
$WORKSPACE/tools/virsh/ssh.sh $TARGET /root/promenade/validate-$TARGET.sh

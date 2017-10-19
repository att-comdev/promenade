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

$SCRIPT_DIR/ssh.sh $TARGET promenade-teardown
$SCRIPT_DIR/ssh.sh $API kubectl delete node $TARGET

$SCRIPT_DIR/destroy.sh $TARGET
$SCRIPT_DIR/create.sh $TARGET
$SCRIPT_DIR/push-example-scripts.sh $TARGET

$SCRIPT_DIR/ssh.sh $TARGET /root/promenade/join-$TARGET.sh
$SCRIPT_DIR/ssh.sh $TARGET /root/promenade/validate-$TARGET.sh

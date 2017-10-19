#!/usr/bin/env bash

set -ex

SCRIPT_DIR=$(realpath $(dirname $0))

$SCRIPT_DIR/destroy.sh
$SCRIPT_DIR/create.sh
$SCRIPT_DIR/push-example-scripts.sh $TARGET

$SCRIPT_DIR/ssh.sh n0 /root/promenade/genesis.sh
$SCRIPT_DIR/ssh.sh n0 /root/promenade/validate-genesis.sh

$SCRIPT_DIR/ssh.sh n1 /root/promenade/join-n1.sh
$SCRIPT_DIR/ssh.sh n1 /root/promenade/validate-n1.sh
$SCRIPT_DIR/ssh.sh n2 /root/promenade/join-n2.sh
$SCRIPT_DIR/ssh.sh n2 /root/promenade/validate-n2.sh

$SCRIPT_DIR/reprovision.sh n0 n1

$SCRIPT_DIR/ssh.sh n3 /root/promenade/join-n3.sh
$SCRIPT_DIR/ssh.sh n3 /root/promenade/validate-n3.sh

$SCRIPT_DIR/ssh.sh n1 /root/promenade/validate-cluster.sh

$SCRIPT_DIR/stop.sh
$SCRIPT_DIR/start.sh

$SCRIPT_DIR/ssh.sh n1 /root/promenade/validate-cluster.sh

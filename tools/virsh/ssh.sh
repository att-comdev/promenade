#!/usr/bin/env bash

set -e

SSH_CONFIG_DIR=$(realpath $(dirname $0))/config-ssh

exec ssh -F $SSH_CONFIG_DIR/config $@

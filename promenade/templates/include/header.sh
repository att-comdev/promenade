#!/usr/bin/env bash

set -e

{% include "utils.sh" with context %}

# Validate the hostname is as expected
#
if [ "$(hostname)" != "{{ config.get_first('Genesis:hostname', 'KubernetesNode:hostname') }}" ]; then
   echo "The node hostname must match the Kubernetes node name" 1>&2
   exit 1
fi

# Ensure the script is running as root.
#
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root." 1>&2
   exit 1
fi

function log {
    echo $(date) $* 1>&2
}

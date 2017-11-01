#!/bin/sh
# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -x

export MANIFEST_PATH=/host{{ .Values.anchor.kubelet.manifest_path }}/{{ .Values.service.name }}.yaml
export PKI_PATH=/host{{ .Values.apiserver.host_etc_path }}/pki

copy_certificates() {
    mkdir -p $PKI_PATH
    cp /certs/* /keys/* $PKI_PATH
}

create_manifest() {
    mkdir -p $(dirname $MANIFEST_PATH)
    cp /tmp/etc/kubernetes-apiserver.yaml $MANIFEST_PATH
}

cleanup() {
    rm -f $MANIFEST_PATH
    rm -rf $PKI_PATH
}

while true; do
    if [ -e /tmp/stop ]; then
        echo Stopping
        cleanup
        break
    fi

    if [ ! -e $MANIFEST_PATH ]; then
        copy_certificates
        create_manifest
    fi

    sleep {{ .Values.anchor.period }}
done

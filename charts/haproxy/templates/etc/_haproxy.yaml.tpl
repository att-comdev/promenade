{{/*
Copyright 2018 AT&T Intellectual Property.  All other rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/}}
---
apiVersion: v1
kind: Pod
metadata:
  name: haproxy
  namespace: {{ .Release.Namespace }}
spec:
  hostNetwork: true
  containers:
    - name: haproxy
      image: {{ .Values.images.tags.haproxy }}
      imagePullPolicy: {{ .Values.images.pull_policy }}
      hostNetwork: true
      env:
        - name: HAPROXY_CONF
          value: {{ .Values.conf.haproxy.container_config_dir }}/haproxy.cfg
        - name: BACKUP
          value: /tmp/backup.cfg
      command:
        - /bin/sh
        - -c
        - |
            set -eux

            while [ ! -s "$HAPROXY_CONF" ]; do
                echo Waiting for "HAPROXY_CONF"
                sleep 1
            done
            cp "$HAPROXY_CONF" "$BACKUP"

            haproxy -f "$HAPROXY_CONF" &

            set +x
            while true; do
                if ! cmp -s "$HAPROXY_CONF" "$BACKUP"; then
                    cp "$HAPROXY_CONF" "$BACKUP"
                    kill -HUP %1
                fi
                sleep {{ .Values.conf.haproxy.period }}
            done

      volumeMounts:
        - name: etc
          mountPath: {{ .Values.conf.haproxy.container_config_dir }}
  volumes:
    - name: etc
      hostPath:
        path: {{ .Values.conf.haproxy.host_config_dir }}

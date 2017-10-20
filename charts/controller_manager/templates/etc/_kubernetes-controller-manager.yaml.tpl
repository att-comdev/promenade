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

---
apiVersion: v1
kind: Pod
metadata:
  name: {{ .Values.service.name }}
  namespace: {{ .Release.Namespace }}
  labels:
    {{ .Values.service.name }}-service: enabled
spec:
  hostNetwork: true
  containers:
    - name: controller-manager
      image: {{ .Values.images.controller_manager }}
      env:
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
      command:
        - {{ .Values.controller_manager.command }}
        - --allocate-node-cidrs=true
        - --cluster-cidr={{ .Values.network.pod_cidr }}
        - --configure-cloud-routes=false
        - --leader-elect=true
        - --node-monitor-period={{ .Values.controller_manager.node_monitor_period }}
        - --node-monitor-grace-period={{ .Values.controller_manager.node_monitor_grace_period }}
        - --pod-eviction-timeout={{ .Values.controller_manager.pod_eviction_timeout }}
        - --kubeconfig=/etc/kubernetes/controller-manager/kubeconfig.yaml
        - --root-ca-file=/etc/kubernetes/controller-manager/cluster-ca.pem
        - --service-account-private-key-file=/etc/kubernetes/controller-manager/service-account.priv
        - --service-cluster-ip-range={{ .Values.network.service_cidr }}
        - --use-service-account-credentials=true

        - --v=5

      volumeMounts:
        - name: etc
          mountPath: /etc/kubernetes/controller-manager
  volumes:
    - name: etc
      hostPath:
        path: {{ .Values.controller_manager.host_etc_path }}

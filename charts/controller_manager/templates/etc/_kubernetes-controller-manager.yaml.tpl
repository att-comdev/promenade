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
      image: {{ .Values.images.tags.controller_manager }}
      env:
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
      command:
        - {{ .Values.controller_manager.command_prefix }}
        - --allocate-node-cidrs={{ .Values.controller_manager.command_suffix.allocate_node_cidrs }}
        - --cluster-cidr={{ .Values.controller_manager.command_suffix.cluster_cidr }}
        - --configure-cloud-routes={{ .Values.controller_manager.command_suffix.configure_cloud_routes }}
        - --leader-elect={{ .Values.controller_manager.command_suffix.leader_elect }}
        - --node-monitor-period={{ .Values.controller_manager.command_suffix.node_monitor_period }}
        - --node-monitor-grace-period={{ .Values.controller_manager.command_suffix.node_monitor_grace_period }}
        - --pod-eviction-timeout={{ .Values.controller_manager.command_suffix.pod_eviction_timeout }}
        - --kubeconfig={{ .Values.controller_manager.command_suffix.kubeconfig }}
        - --root-ca-file={{ .Values.controller_manager.command_suffix.root_ca_file }}
        - --service-account-private-key-file={{ .Values.controller_manager.command_suffix.service_account_private_key_file }}
        - --service-cluster-ip-range={{ .Values.controller_manager.command_suffix.service_cluster_ip_range }}
        - --use-service-account-credentials={{ .Values.controller_manager.command_suffix.use_service_account_credentials }}
        - --v={{ .Values.controller_manager.command_suffix.v }}

      volumeMounts:
        - name: etc
          mountPath: /etc/kubernetes/controller-manager
  volumes:
    - name: etc
      hostPath:
        path: {{ .Values.controller_manager.host_etc_path }}

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

{{- if .Values.manifests.service }}
{{- $envAll := . }}
---
apiVersion: v1
kind: Pod
metadata:
  name: {{ .Values.service.name }}
  namespace: {{ .Release.Namespace }}
  labels:
{{ tuple $envAll "kubernetes-apiserver" "service" | include "helm-toolkit.snippets.kubernetes_metadata_labels" | indent 4 }}
spec:
  hostNetwork: true
  containers:
    - name: apiserver
      image: {{ .Values.images.tags.apiserver }}
      env:
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
      command:
        - {{ .Values.apiserver.command }}
        - --authorization-mode=Node,RBAC
        - --advertise-address=\$(POD_IP)
        - --admission-control=NamespaceLifecycle,LimitRanger,ServiceAccount,PersistentVolumeLabel,DefaultStorageClass,ResourceQuota,DefaultTolerationSeconds
        - --anonymous-auth=false
        - --bind-address=0.0.0.0
        - --secure-port={{ .Values.apiserver.port }}
        - --insecure-port=0
        - --apiserver-count={{ .Values.apiserver.replicas }}

        - --client-ca-file=/etc/kubernetes/apiserver/pki/cluster-ca.pem
        - --tls-cert-file=/etc/kubernetes/apiserver/pki/apiserver.pem
        - --tls-private-key-file=/etc/kubernetes/apiserver/pki/apiserver-key.pem

        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
        - --kubelet-certificate-authority=/etc/kubernetes/apiserver/pki/cluster-ca.pem
        - --kubelet-client-certificate=/etc/kubernetes/apiserver/pki/apiserver.pem
        - --kubelet-client-key=/etc/kubernetes/apiserver/pki/apiserver-key.pem

        - --etcd-servers={{ .Values.apiserver.etcd.endpoints }}
        - --etcd-cafile=/etc/kubernetes/apiserver/pki/etcd-client-ca.pem
        - --etcd-certfile=/etc/kubernetes/apiserver/pki/etcd-client.pem
        - --etcd-keyfile=/etc/kubernetes/apiserver/pki/etcd-client-key.pem

        - --allow-privileged=true

        - --service-cluster-ip-range={{ .Values.network.service_cidr }}
        - --service-account-key-file=/etc/kubernetes/apiserver/pki/service-account.pub

        - --v=5

      ports:
        - containerPort: {{ .Values.apiserver.port }}
      volumeMounts:
        - name: etc
          mountPath: /etc/kubernetes/apiserver
  volumes:
    - name: etc
      hostPath:
        path: {{ .Values.apiserver.host_etc_path }}
{{- end }}

# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from promenade import exceptions, logging
import abc
import copy
import kubernetes

LOG = logging.getLogger(__name__)


class IStatusManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_current_status(self):
        pass

    @abc.abstractmethod
    def set_service_statuses(self):
        pass


class KubernetesStatusManager(IStatusManager):
    GROUP = 'promenade.ucp.att.com'
    VERSION = 'v1'
    PLURAL = 'node-statuses'
    KIND = 'NodeStatus'

    def __init__(self, *, hostname):
        self.ext_client = kubernetes.client.ApiextensionsV1beta1Api()
        self.crd_client = kubernetes.client.CustomObjectsApi()

        self.hostname = hostname
        self._latest_doc = None

    def get_current_status(self):
        doc = self._get_current_doc()
        return {
            'services': doc.get('services', {}),
        }

    def _get_current_doc(self):
        doc = self._get_upstream_doc()
        if doc is None:
            doc = self._blank_doc()
        self._latest_doc = doc
        return doc

    def _get_upstream_doc(self):
        self._verify_crd_present()
        try:
            return self.crd_client.get_cluster_custom_object(
                self.GROUP, self.VERSION, self.PLURAL, self.hostname)
        except kubernetes.client.rest.ApiException as e:
            if getattr(e, 'status') != 404:
                LOG.exceptions('Failed to fetch custom node status doc for %s',
                               self.hostname)
                raise exceptions.KubernetesApiError()

    def _verify_crd_present(self):
        crd_name = '%s.%s' % (self.PLURAL, self.GROUP)
        try:
            self.ext_client.read_custom_resource_definition(
                crd_name, exact=True)
        except kubernetes.client.rest.ApiException as e:
            LOG.exception('Failed to find CRD: %s', crd_name)
            raise exceptions.KubernetesCRDVerifyFailure()

    def set_service_statuses(self, statuses):
        if self._latest_doc is None:
            raise exceptions.StatusLogicError(
                'You must get node status before you can attempt to set it.')
        new_doc = copy.deepcopy(self._latest_doc)
        new_doc['services'] = {}
        for name, status in statuses.items():
            new_doc['services'][name] = status

        self._apply_doc(new_doc)

        self._get_current_doc()

    def _apply_doc(self, new_doc):
        try:
            self.crd_client.replace_cluster_custom_object(
                self.GROUP, self.VERSION, self.PLURAL, self.hostname, new_doc)
        except kubernetes.client.rest.ApiException as replace_exc:
            if replace_exc.status == 404:
                try:
                    self.crd_client.create_cluster_custom_object(
                        self.GROUP, self.VERSION, self.PLURAL, new_doc)
                except kubernetes.client.rest.ApiException as create_exc:
                    LOG.exception('Failed to create node statuses doc for %s',
                                  self.hostname)
                    raise exceptions.KubernetesApiError()
            else:
                LOG.exception(
                    'Failed to replace existing node statuses doc for %s',
                    self.hostname)
                raise exceptions.KubernetesApiError()

    def _blank_doc(self):
        return {
            'apiVersion': '%s/%s' % (self.GROUP, self.VERSION),
            'kind': self.KIND,
            'metadata': {
                'name': self.hostname,
            },
            'services': {},
        }

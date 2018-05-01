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

from promenade import logging
import abc
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

    def get_current_status(self):
        status = self._get_upstream_status()
        if status is None:
            status = self._blank_doc()
        return status

    def _get_upstream_status(self):
        self._verify_crd_present()
        # self.ext_client

    def _verify_crd_present(self):
        # TODO(mark-burnett): raise exception if cannot verify crd
        LOG.info('%s', self.ext_client.get_custom_resource_definition(
            '%s.%s' % (self.PLURAL, self.GROUP), exact=True, export=True))

    def set_service_statuses(self, statuses):
        pass
        #raise NotImplementedError('oh dear')

    def _blank_doc(self):
        return {
            'apiVersion': '%s/%s' % (self.GROUP, self.VERSION),
            'kind': self.KIND,
            'metadata': {
                'name': self.hostname,
            },
            'services': {},
        }

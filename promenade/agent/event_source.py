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
import kubernetes

LOG = logging.getLogger(__name__)


class IEventSource(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def stream_events(self):
        pass


class KubernetesEventSource(IEventSource):
    GROUP = 'promenade.ucp.att.com'
    VERSION = 'v1'
    PLURAL = 'nodes'

    def __init__(self):
        try:
            kubernetes.config.load_incluster_config()
            LOG.info('Loaded in-cluster Kubernetes configuration.')
        except kubernetes.config.config_exception.ConfigException:
            LOG.debug('Failed to load in-cluster configuration')
            kubernetes.config.load_kube_config()
            LOG.info('Loaded out-of-cluster Kubernetes configuration.')

        self.ext_client = kubernetes.client.ApiextensionsV1beta1Api()
        self.crd_client = kubernetes.client.CustomObjectsApi()

    def stream_events(self):
        self._wait_for_resource_definitions()
        LOG.info('Monitoring events')

        stream = kubernetes.watch.Watch().stream(
            self.crd_client.list_cluster_custom_object, self.GROUP,
            self.VERSION, self.PLURAL)
        for event in stream:
            yield event

    @property
    def _expected_crds(self):
        return {self.GROUP + '/' + self.VERSION + ':' + self.PLURAL}

    def _wait_for_resource_definitions(self):
        expected_crds = self._expected_crds
        seen_crds = set()

        LOG.info('Waiting for presence of expected CRDs')
        watch = kubernetes.watch.Watch()
        stream = watch.stream(self.ext_client.list_custom_resource_definition)

        for event in stream:
            type_ = event['type'].upper()
            crd_name = _concat_crd_name(event['raw_object'])
            if type_ in {'ADDED', 'MODIFIED'}:
                LOG.debug('Found CRD: %s', crd_name)
                seen_crds.add(crd_name)
            elif type_ == 'DELETED':
                LOG.debug('Removed CRD: %s', crd_name)
                seen_crds.remove(crd_name)
            elif type_ == 'ERROR':
                LOG.error('Got an error event from the Kubernetes API: %s',
                          event)
                raise exceptions.KubernetesErrorEvent()
            else:
                LOG.error('Got unexpected event from Kubernets API: %s', event)
                raise exceptions.KubernetesUnexpectedEvent()

            if seen_crds.issubset(expected_crds):
                LOG.info('Found expected CRDs: %s', expected_crds)
                watch.stop()
            else:
                LOG.debug('Still waiting for CRDs: %s',
                          seen_crds - expected_crds)


def _concat_crd_name(crd):
    spec = crd.get('spec', {})
    return '%s/%s:%s' % (spec.get('group'), spec.get('version'),
                         spec.get('names', {}).get('plural'))

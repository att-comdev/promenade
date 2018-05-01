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
import kubernetes

LOG = logging.getLogger(__name__)


class KubernetesWrapper:
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

    def get_custom_object(self, group, version, plural, name):
        try:
            doc = self.crd_client.get_cluster_custom_object(
                group, version, plural, name)
            LOG.debug('Got custom document (%s, %s, %s, %s): %s', group,
                      version, plural, name, doc)
            return doc
        except kubernetes.client.rest.ApiException as e:
            if getattr(e, 'status') != 404:
                LOG.exception(
                    'Failed to fetch custom document (%s, %s, %s, %s)', group,
                    version, plural, name)
                raise exceptions.KubernetesApiError()

    def put_custom_object(self, group, version, plural, name, body):
        try:
            self.crd_client.replace_cluster_custom_object(
                group, version, plural, name, body)
            LOG.info('Updated custom resource: (%s, %s, %s, %s)', group,
                     version, plural, name)
            LOG.debug('Updated body for (%s, %s, %s, %s) to: %s', group,
                      version, plural, name, body)
        except kubernetes.client.rest.ApiException as replace_exc:
            if replace_exc.status == 404:
                try:
                    self.crd_client.create_cluster_custom_object(
                        group, version, plural, body)
                    LOG.info('Created custom resource: (%s, %s, %s, %s)',
                             group, version, plural, name)
                    LOG.debug('Created body for (%s, %s, %s, %s) to: %s',
                              group, version, plural, name, body)
                except kubernetes.client.rest.ApiException as create_exc:
                    LOG.exception(
                        'Failed to create custom resource (%s, %s, %s, %s)',
                        group, version, plural, name)
                    raise exceptions.KubernetesApiError()
            else:
                LOG.exception('Failed to replace existing custom resource '
                              '(%s, %s, %s, %s): %s', group, version, plural,
                              name, body)
                raise exceptions.KubernetesApiError()

    def stream_custom_objects(self, group, version, plural):
        return kubernetes.watch.Watch().stream(
            self.crd_client.list_cluster_custom_object, group, version, plural)

    def verify_crds(self, crd_names):
        missing_crds = set()
        for crd_name in crd_names:
            try:
                LOG.debug('Checking for crd: %s', crd_name)
                self.ext_client.read_custom_resource_definition(
                    crd_name, exact=True)
            except kubernetes.client.rest.ApiException as e:
                LOG.exception('Failed to find CRD: %s', crd_name)
                missing_crds.add(crd_name)

        if missing_crds:
            raise exceptions.KubernetesCRDVerifyFailure(
                'Failed to find crds: %s' % sorted(missing_crds))

    def wait_for_crds(self, crd_names):
        expected_crds = set(crd_names)
        seen_crds = set()

        LOG.info('Waiting for presence of expected CRDs')
        w = _create_watch()

        for event in w.stream(self.ext_client.list_custom_resource_definition):
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

            if expected_crds.issubset(seen_crds):
                LOG.info('Found expected CRDs: %s', expected_crds)
                w.stop()
            else:
                LOG.debug('Still waiting for CRDs: %s (seen=%s, expected=%s)',
                          seen_crds - expected_crds, seen_crds, expected_crds)

        remaining_crds = expected_crds - seen_crds
        if remaining_crds:
            LOG.error('Stream ended while still expecting crds: %s '
                      '(seen=%s, expected=%s)', remaining_crds, seen_crds,
                      expected_crds)
            raise exceptions.KubernetesEarlyStreamReturn()
        else:
            LOG.info('Done waiting for CRDs')


def _create_watch():
    return kubernetes.watch.Watch()


def _concat_crd_name(crd):
    spec = crd.get('spec', {})
    return '%s/%s:%s' % (spec.get('group'), spec.get('version'),
                         spec.get('names', {}).get('plural'))

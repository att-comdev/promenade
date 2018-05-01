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

from promenade import exceptions
from promenade.agent import kube_util
from unittest import mock
import kubernetes
import pytest

BASE_PATCH_PATH = 'promenade.agent.kube_util.kubernetes'
GROUP = 'promenade.airshipit.org'
VERSION = 'v1'
PLURAL = 'node-statuses'

CRD_NAMES = [
    'node-configurations.promenade.airshipit.org',
    'node-statuses.promenade.airshipit.org',
]

CRD_FULL_NAMES = [
    'promenade.airshipit.org/v1:node-configurations',
    'promenade.airshipit.org/v1:node-statuses',
]

VALID_NODE_STATUS = {
    'apiVersion': GROUP + '/' + VERSION,
    'kind': 'NodeStatus',
    'metadata': {
        'name': 'n0',
    },
    'services': {
        'docker': 'active',
    },
}


def test_init_incluster():
    with mock.patch(BASE_PATCH_PATH) as k:
        kube_util.KubernetesWrapper()

        assert k.config.load_incluster_config.call_count == 1
        k.config.load_kube_config.assert_not_called()


def test_init_kube_config():
    with mock.patch(BASE_PATCH_PATH + '.config.load_incluster_config') as i:
        i.side_effect = kubernetes.config.config_exception.ConfigException
        with mock.patch(BASE_PATCH_PATH + '.config.load_kube_config') as k:
            kube_util.KubernetesWrapper()

            assert i.call_count == 1
            assert k.call_count == 1


def test_get_custom_object_found():
    with mock.patch(BASE_PATCH_PATH):
        w = kube_util.KubernetesWrapper()

        w.crd_client.get_cluster_custom_object.return_value = VALID_NODE_STATUS

        doc = w.get_custom_object(GROUP, VERSION, PLURAL, 'n0')
        w.crd_client.get_cluster_custom_object.assert_called_once_with(
            GROUP, VERSION, PLURAL, 'n0')

        assert doc == VALID_NODE_STATUS


def test_get_custom_object_not_found():
    exc_class = kubernetes.client.rest.ApiException

    with mock.patch(BASE_PATCH_PATH + '.config'):
        with mock.patch(BASE_PATCH_PATH + '.client.CustomObjectsApi'):
            w = kube_util.KubernetesWrapper()

            w.crd_client.get_cluster_custom_object.side_effect = exc_class(
                status=404)

            doc = w.get_custom_object(GROUP, VERSION, PLURAL, 'n0')
            w.crd_client.get_cluster_custom_object.assert_called_once_with(
                GROUP, VERSION, PLURAL, 'n0')

            assert doc == None


def test_get_custom_object_unknown_error():
    exc_class = kubernetes.client.rest.ApiException

    with mock.patch(BASE_PATCH_PATH + '.config'):
        with mock.patch(BASE_PATCH_PATH + '.client.CustomObjectsApi'):
            w = kube_util.KubernetesWrapper()

            w.crd_client.get_cluster_custom_object.side_effect = exc_class(
                status=500)

            with pytest.raises(exceptions.KubernetesApiError):
                w.get_custom_object(GROUP, VERSION, PLURAL, 'n0')

            w.crd_client.get_cluster_custom_object.assert_called_once_with(
                GROUP, VERSION, PLURAL, 'n0')


def test_put_custom_object_create_success():
    exc_class = kubernetes.client.rest.ApiException

    with mock.patch(BASE_PATCH_PATH + '.config'):
        with mock.patch(BASE_PATCH_PATH + '.client.CustomObjectsApi'):
            w = kube_util.KubernetesWrapper()

            w.crd_client.replace_cluster_custom_object.side_effect = exc_class(
                status=404)

            w.put_custom_object(GROUP, VERSION, PLURAL, 'n0', {'foo': 'bar'})

            w.crd_client.create_cluster_custom_object.assert_called_once_with(
                GROUP, VERSION, PLURAL, {
                    'foo': 'bar'
                })
            w.crd_client.replace_cluster_custom_object.assert_called_once_with(
                GROUP, VERSION, PLURAL, 'n0', {
                    'foo': 'bar'
                })


def test_put_custom_object_create_fail():
    exc_class = kubernetes.client.rest.ApiException

    with mock.patch(BASE_PATCH_PATH + '.config'):
        with mock.patch(BASE_PATCH_PATH + '.client.CustomObjectsApi'):
            w = kube_util.KubernetesWrapper()

            w.crd_client.replace_cluster_custom_object.side_effect = exc_class(
                status=404)
            w.crd_client.create_cluster_custom_object.side_effect = exc_class(
                status=500)

            with pytest.raises(exceptions.KubernetesApiError):
                w.put_custom_object(GROUP, VERSION, PLURAL, 'n0', {
                    'foo': 'bar'
                })

            w.crd_client.create_cluster_custom_object.assert_called_once_with(
                GROUP, VERSION, PLURAL, {
                    'foo': 'bar'
                })
            w.crd_client.replace_cluster_custom_object.assert_called_once_with(
                GROUP, VERSION, PLURAL, 'n0', {
                    'foo': 'bar'
                })


def test_put_custom_object_replace_success():
    with mock.patch(BASE_PATCH_PATH):
        w = kube_util.KubernetesWrapper()
        w.put_custom_object(GROUP, VERSION, PLURAL, 'n0', {'foo': 'bar'})

        w.crd_client.create_cluster_custom_object.assert_not_called()
        w.crd_client.replace_cluster_custom_object.assert_called_once_with(
            GROUP, VERSION, PLURAL, 'n0', {
                'foo': 'bar'
            })


def test_put_custom_object_replace_failure():
    exc_class = kubernetes.client.rest.ApiException

    with mock.patch(BASE_PATCH_PATH + '.config'):
        with mock.patch(BASE_PATCH_PATH + '.client.CustomObjectsApi'):
            w = kube_util.KubernetesWrapper()

            w.crd_client.replace_cluster_custom_object.side_effect = exc_class(
                status=500)

            with pytest.raises(exceptions.KubernetesApiError):
                w.put_custom_object(GROUP, VERSION, PLURAL, 'n0', {
                    'foo': 'bar'
                })

            w.crd_client.create_cluster_custom_object.assert_not_called()
            w.crd_client.replace_cluster_custom_object.assert_called_once_with(
                GROUP, VERSION, PLURAL, 'n0', {
                    'foo': 'bar'
                })


def test_verify_crds_all_present():
    with mock.patch(BASE_PATCH_PATH):
        w = kube_util.KubernetesWrapper()
        w.verify_crds(CRD_NAMES)

        assert w.ext_client.read_custom_resource_definition.call_count == 2
        for name in CRD_NAMES:
            w.ext_client.read_custom_resource_definition.assert_any_call(
                name, exact=True)


def test_verify_crds_some_present():
    exc_class = kubernetes.client.rest.ApiException

    with mock.patch(BASE_PATCH_PATH + '.config'):
        with mock.patch(BASE_PATCH_PATH + '.client.ApiextensionsV1beta1Api'):
            w = kube_util.KubernetesWrapper()

        w.ext_client.read_custom_resource_definition.side_effect = [
            exc_class(status=404), None
        ]

        with pytest.raises(exceptions.KubernetesCRDVerifyFailure):
            w.verify_crds(CRD_NAMES)

        assert w.ext_client.read_custom_resource_definition.call_count == 2
        for name in CRD_NAMES:
            w.ext_client.read_custom_resource_definition.assert_any_call(
                name, exact=True)


def test_verify_crds_none_present():
    exc_class = kubernetes.client.rest.ApiException

    with mock.patch(BASE_PATCH_PATH + '.config'):
        with mock.patch(BASE_PATCH_PATH + '.client.ApiextensionsV1beta1Api'):
            w = kube_util.KubernetesWrapper()

        w.ext_client.read_custom_resource_definition.side_effect = exc_class(
            status=404)

        with pytest.raises(exceptions.KubernetesCRDVerifyFailure):
            w.verify_crds(CRD_NAMES)

        assert w.ext_client.read_custom_resource_definition.call_count == 2
        for name in CRD_NAMES:
            w.ext_client.read_custom_resource_definition.assert_any_call(
                name, exact=True)


EVENT_NODE_CONFIGURATIONS_ADDED = {
    'type': 'ADDED',
    'raw_object': {
        'metadata': {
            'name': 'node-configurations.promenade.airshipit.org',
        },
        'spec': {
            'group': 'promenade.airshipit.org',
            'version': 'v1',
            'names': {
                'plural': 'node-configurations',
            },
        },
    },
}

EVENT_NODE_CONFIGURATIONS_DELETED = {
    'type': 'DELETED',
    'raw_object': {
        'metadata': {
            'name': 'node-configurations.promenade.airshipit.org',
        },
        'spec': {
            'group': 'promenade.airshipit.org',
            'version': 'v1',
            'names': {
                'plural': 'node-configurations',
            },
        },
    },
}

EVENT_NODE_STATUSES_MODIFIED = {
    'type': 'MODIFIED',
    'raw_object': {
        'metadata': {
            'name': 'node-statuses.promenade.airshipit.org',
        },
        'spec': {
            'group': 'promenade.airshipit.org',
            'version': 'v1',
            'names': {
                'plural': 'node-statuses',
            },
        },
    },
}

EVENT_CRD_ERROR = {
    'type': 'ERROR',
    'raw_object': {
        'metadata': {
            'name': 'node-configurations.promenade.airshipit.org',
        },
        'spec': {
            'group': 'promenade.airshipit.org',
            'version': 'v1',
            'names': {
                'plural': 'node-configurations',
            },
        },
    },
}

EVENT_CRD_UNKNOWN = {
    'type': 'nonsensetype',
    'raw_object': {
        'metadata': {
            'name': 'node-configurations.promenade.airshipit.org',
        },
        'spec': {
            'group': 'promenade.airshipit.org',
            'version': 'v1',
            'names': {
                'plural': 'node-configurations',
            },
        },
    },
}


def test_wait_for_crds_with_all_valid_events():
    with mock.patch(BASE_PATCH_PATH) as k:
        with mock.patch(
                'promenade.agent.kube_util._create_watch') as create_watch:
            w = kube_util.KubernetesWrapper()

            create_watch.return_value.stream.return_value = [
                EVENT_NODE_CONFIGURATIONS_ADDED,
                EVENT_NODE_STATUSES_MODIFIED,
            ]

            w.wait_for_crds(CRD_FULL_NAMES)


def test_wait_for_crds_with_delete():
    with mock.patch(BASE_PATCH_PATH) as k:
        with mock.patch(
                'promenade.agent.kube_util._create_watch') as create_watch:
            w = kube_util.KubernetesWrapper()

            create_watch.return_value.stream.return_value = [
                EVENT_NODE_CONFIGURATIONS_ADDED,
                EVENT_NODE_CONFIGURATIONS_DELETED,
                EVENT_NODE_STATUSES_MODIFIED,
            ]

            with pytest.raises(exceptions.KubernetesEarlyStreamReturn):
                w.wait_for_crds(CRD_FULL_NAMES)


def test_wait_for_crds_with_error_event():
    with mock.patch(BASE_PATCH_PATH) as k:
        with mock.patch(
                'promenade.agent.kube_util._create_watch') as create_watch:
            w = kube_util.KubernetesWrapper()

            create_watch.return_value.stream.return_value = [
                EVENT_NODE_CONFIGURATIONS_ADDED,
                EVENT_CRD_ERROR,
                EVENT_NODE_STATUSES_MODIFIED,
            ]

            with pytest.raises(exceptions.KubernetesErrorEvent):
                w.wait_for_crds(CRD_FULL_NAMES)


def test_wait_for_crds_with_unknown_event():
    with mock.patch(BASE_PATCH_PATH) as k:
        with mock.patch(
                'promenade.agent.kube_util._create_watch') as create_watch:
            w = kube_util.KubernetesWrapper()

            create_watch.return_value.stream.return_value = [
                EVENT_NODE_CONFIGURATIONS_ADDED,
                EVENT_CRD_UNKNOWN,
                EVENT_NODE_STATUSES_MODIFIED,
            ]

            with pytest.raises(exceptions.KubernetesUnexpectedEvent):
                w.wait_for_crds(CRD_FULL_NAMES)


def test_wait_for_crds_with_early_return():
    with mock.patch(BASE_PATCH_PATH) as k:
        with mock.patch(
                'promenade.agent.kube_util._create_watch') as create_watch:
            w = kube_util.KubernetesWrapper()

            create_watch.return_value.stream.return_value = []

            with pytest.raises(exceptions.KubernetesEarlyStreamReturn):
                w.wait_for_crds(CRD_FULL_NAMES)

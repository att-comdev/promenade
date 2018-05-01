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
GROUP = 'promenade.ucp.att.com'
VERSION = 'v1'
PLURAL = 'node-statuses'


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
    with mock.patch(BASE_PATCH_PATH) as k:
        w = kube_util.KubernetesWrapper()

        w.crd_client.get_cluster_custom_object.return_value = VALID_NODE_STATUS

        doc = w.get_custom_object(GROUP, VERSION, PLURAL, 'n0')
        w.crd_client.get_cluster_custom_object.assert_called_once_with(GROUP,
                VERSION, PLURAL, 'n0')

        assert doc == VALID_NODE_STATUS


def test_get_custom_object_not_found():
    exc_class = kubernetes.client.rest.ApiException

    with mock.patch(BASE_PATCH_PATH + '.config'):
        with mock.patch(BASE_PATCH_PATH + '.client.CustomObjectsApi') as k:
            w = kube_util.KubernetesWrapper()

            w.crd_client.get_cluster_custom_object.side_effect = exc_class(status=404)

            doc = w.get_custom_object(GROUP, VERSION, PLURAL, 'n0')
            w.crd_client.get_cluster_custom_object.assert_called_once_with(GROUP,
                    VERSION, PLURAL, 'n0')

            assert doc == None


def test_get_custom_object_unknown_error():
    exc_class = kubernetes.client.rest.ApiException

    with mock.patch(BASE_PATCH_PATH + '.config'):
        with mock.patch(BASE_PATCH_PATH + '.client.CustomObjectsApi') as k:
            w = kube_util.KubernetesWrapper()

            w.crd_client.get_cluster_custom_object.side_effect = exc_class(status=500)

            with pytest.raises(exceptions.KubernetesApiError):
                w.get_custom_object(GROUP, VERSION, PLURAL, 'n0')

            w.crd_client.get_cluster_custom_object.assert_called_once_with(GROUP,
                    VERSION, PLURAL, 'n0')

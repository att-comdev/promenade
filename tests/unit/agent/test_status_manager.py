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
from promenade.agent import status_manager, kube_util
from unittest import mock
import copy
import pytest


@pytest.fixture
def kube_wrapper():
    return mock.MagicMock(kube_util.KubernetesWrapper)


@pytest.fixture
def sm(kube_wrapper):
    return status_manager.KubernetesStatusManager(
        hostname='n0', kube_wrapper=kube_wrapper)


VALID_STATUS = {
    'apiVersion': 'promenade.airshipit.org/v1',
    'kind': 'NodeStatus',
    'metadata': {
        'name': 'n0',
    },
    'services': {
        'docker': 'active',
    },
}


def test_get_current_status_with_existing_status(kube_wrapper, sm):
    kube_wrapper.get_custom_object.return_value = VALID_STATUS
    status = sm.get_current_status()

    assert kube_wrapper.get_custom_object.call_count == 1
    assert status == {'services': {'docker': 'active'}}


def test_get_current_status_with_no_existing_status(kube_wrapper, sm):
    kube_wrapper.get_custom_object.return_value = None
    status = sm.get_current_status()

    assert kube_wrapper.get_custom_object.call_count == 1
    assert status == {'services': {}}


def test_set_current_status_with_existing_status(kube_wrapper, sm):
    kube_wrapper.get_custom_object.return_value = VALID_STATUS
    sm.get_current_status()

    sm.set_service_statuses({'kubelet': 'active'})
    expected_doc = copy.deepcopy(VALID_STATUS)
    expected_doc['services'] = {'kubelet': 'active'}

    assert kube_wrapper.get_custom_object.call_count == 1
    assert kube_wrapper.put_custom_object.call_count == 1
    kube_wrapper.put_custom_object.assert_called_once_with(
        'promenade.airshipit.org', 'v1', 'node-statuses', 'n0', expected_doc)


def test_set_current_status_with_no_existing_status(kube_wrapper, sm):
    kube_wrapper.get_custom_object.return_value = None
    sm.get_current_status()

    sm.set_service_statuses({'kubelet': 'active'})
    expected_doc = copy.deepcopy(VALID_STATUS)
    expected_doc['services'] = {'kubelet': 'active'}

    assert kube_wrapper.get_custom_object.call_count == 1
    assert kube_wrapper.put_custom_object.call_count == 1
    kube_wrapper.put_custom_object.assert_called_once_with(
        'promenade.airshipit.org', 'v1', 'node-statuses', 'n0', expected_doc)


def test_set_current_status_without_calling_get(kube_wrapper, sm):
    with pytest.raises(exceptions.StatusLogicError):
        sm.set_service_statuses({'kubelet': 'active'})

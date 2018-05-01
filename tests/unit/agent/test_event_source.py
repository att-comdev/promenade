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
from promenade.agent import event_source, kube_util
from unittest import mock
import pytest


@pytest.fixture
def kube_wrapper():
    return mock.MagicMock(kube_util.KubernetesWrapper)


@pytest.fixture
def es(kube_wrapper):
    return event_source.KubernetesEventSource(
        hostname='n0', kube_wrapper=kube_wrapper)


EVENT_HOSTNAME_DIFFERENT = {
    'type': 'MODIFIED',
    'raw_object': {
        'metadata': {
            'name': 'n1',
        },
        'foo': 'bar',
    }
}

EVENT_HOSTNAME_MISSING = {
    'type': 'ADDED',
    'raw_object': {
        'foo': 'bar',
    }
}

EVENT_LOCAL_ADDED = {
    'type': 'ADDED',
    'raw_object': {
        'metadata': {
            'name': 'n0',
        },
        'foo': 'bar',
    }
}

EVENT_LOCAL_DELETED = {
    'type': 'DELETED',
    'raw_object': {
        'metadata': {
            'name': 'n0',
        },
    }
}

EVENT_LOCAL_MODIFIED = {
    'type': 'MODIFIED',
    'raw_object': {
        'metadata': {
            'name': 'n0',
        },
        'foo': 'bar',
        'baz': 'buz',
    }
}


def test_filter_with_valid_events(es, kube_wrapper):
    input_events = [
        EVENT_LOCAL_ADDED,
        EVENT_LOCAL_MODIFIED,
        EVENT_LOCAL_DELETED,
        EVENT_HOSTNAME_DIFFERENT,
        EVENT_HOSTNAME_MISSING,
    ]

    expected_events = [
        EVENT_LOCAL_ADDED['raw_object'],
        EVENT_LOCAL_MODIFIED['raw_object'],
    ]

    kube_wrapper.stream_custom_objects.return_value = input_events
    output_events = list(es.stream_events())

    kube_wrapper.stream_custom_objects.assert_called_once_with(
        'promenade.ucp.att.com', 'v1', 'node-configurations')
    assert output_events == expected_events


def test_filter_error_event(es, kube_wrapper):
    kube_wrapper.stream_custom_objects.return_value = [
        {
            'type': 'ERROR',
            'object': {
                'metadata': {
                    'name': 'n0',
                },
                'foo': 'bar',
            },
        },
    ]

    with pytest.raises(exceptions.KubernetesErrorEvent):
        list(es.stream_events())


def test_filter_unknown_event(es, kube_wrapper):
    kube_wrapper.stream_custom_objects.return_value = [
        {
            'type': 'nonsense',
            'object': {
                'metadata': {
                    'name': 'n0',
                },
                'foo': 'bar',
            },
        },
    ]

    with pytest.raises(exceptions.KubernetesUnexpectedEvent):
        list(es.stream_events())

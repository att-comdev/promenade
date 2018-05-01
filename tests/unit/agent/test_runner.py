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
from promenade.agent import engine
from promenade.agent.runner import AgentRunner
from promenade.agent.event_source import IEventSource
from unittest import mock
import pytest


@pytest.fixture
def eng():
    return mock.MagicMock(engine.AgentEngine)


LOCAL_EVENT = {
    'type': 'ADDED',
    'object': {
        'metadata': {
            'name': 'n0',
        },
        'foo': 'bar',
    },
}


@pytest.fixture
def es():
    event_source = mock.MagicMock(IEventSource)
    event_source.stream_events.return_value = [
        LOCAL_EVENT,
        {
            'type': 'ADDED',
            'object': {
                'metadata': {
                    'name': 'n1',
                },
                'foo': 'bar',
            },
        },
    ]

    return event_source


@pytest.fixture
def runner(eng, es):
    return AgentRunner(engine=eng, event_source=es, hostname='n0')


def test_handle_stream(runner, eng):
    runner.handle_stream()

    eng.apply.assert_called_once_with(LOCAL_EVENT['object'])


def test_handle_event_added(runner, eng):
    event = {
        'type': 'ADDED',
        'object': {
            'metadata': {
                'name': 'n0',
            },
            'foo': 'bar',
        },
    }

    runner.handle_event(event)
    eng.apply.assert_called_once_with(event['object'])


def test_handle_event_modified(runner, eng):
    event = {
        'type': 'MODIFIED',
        'object': {
            'metadata': {
                'name': 'n0',
            },
            'foo': 'bar',
        },
    }

    runner.handle_event(event)
    eng.apply.assert_called_once_with(event['object'])


def test_handle_event_deleted(runner, eng):
    event = {
        'type': 'DELETED',
        'object': {
            'metadata': {
                'name': 'n0',
            },
            'foo': 'bar',
        },
    }

    runner.handle_event(event)
    eng.apply.assert_not_called()


def test_handle_event_error(runner, eng):
    event = {
        'type': 'ERROR',
        'object': {
            'metadata': {
                'name': 'n0',
            },
            'foo': 'bar',
        },
    }

    with pytest.raises(exceptions.KubernetesErrorEvent):
        runner.handle_event(event)


def test_handle_event_unknown(runner, eng):
    event = {
        'object': {
            'metadata': {
            },
        },
    }

    with pytest.raises(exceptions.KubernetesUnexpectedEvent):
        runner.handle_event(event)
